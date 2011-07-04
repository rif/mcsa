# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
T.current_language=['en', 'en-us']
if session._lang:
    T.force(session._lang)
else:
    T.force(T.accepted_language)

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

if request.env.web2py_runtime_gae:            # if running on Google App Engine
    db = DAL('gae')                           # connect to Google BigTable
                                              # optional DAL('gae://namespace')
    session.connect(request, response, db = db) # and store sessions and tickets there
    ### or use the following lines to store sessions in Memcache
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
else:                                         # else use a normal relational database
    db = DAL('sqlite://storage.sqlite', migrate_enabled=True)       # if not, use SQLite or other DB
## if no need for session
# session.forget()

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import *
mail = Mail()                                  # mailer
auth = Auth(globals(),db)                      # authentication/authorization
crud = Crud(globals(),db)                      # for CRUD helpers using auth
service = Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()

mail.settings.server = 'logging' or 'smtp.gmail.com:587'  # your SMTP server
mail.settings.sender = 'ustest@gmail.com'         # your email
mail.settings.login = 'ustest:greta.1'      # your credentials or None

auth.settings.hmac_key = 'sha512:1000c256-92f1-42b8-9808-ed48e41ccf3b'   # before define_tables()
auth.define_tables()                           # creates all needed tables
auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['reset_password'])+'/%(key)s to reset your password'

#########################################################################
## If you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, uncomment and customize following
# from gluon.contrib.login_methods.rpx_account import RPXAccount
# auth.settings.actions_disabled=['register','change_password','request_reset_password']
# auth.settings.login_form = RPXAccount(request, api_key='...',domain='...',
#    url = "http://localhost:8000/%s/default/user/login" % request.application)
## other login methods are in gluon/contrib/login_methods
#########################################################################

auth.settings.actions_disabled=['register']

crud.settings.auth = None                      # =auth to enforce authorization on crud

class Float_validator:
    def __init__(self, err=T('Float with one decimal in range 0.1 to 24')):
        self.e = err

    def __call__(self, value):
        try:
            value = float(value)
        except ValueError:
            return (value, self.e)
        if (float('%.1f' % value) == value) and (0.1<= value <=24):
            return (value, None)
        return (value, self.e)

    def formatter(self, value):
        return float('%.1f' % float(value))


def cost(row):
    rate = 0.0
    delta = row.end - row.start
    minutes = delta.days * 24 * 60 + delta.seconds / 60
    duration = minutes / 6 * 0.1
    if row.rate:
        rate = row.rate
    else:
        project = db(db.project.id==row.project).select()[0]
        rate = project.rate
    if duration and row.billable:
        return duration * rate
    return 0

db.define_table('perm',
                Field('user', db.auth_user, unique=True),
                Field('auth_list', 'list:reference auth_user', comment=T('Allway put the user itself in the authority list'), label=T('Authority list'))
                )

current_user_perm = db.perm(db.perm.user == auth.user_id)

db.define_table('client',
                Field('name', required=True, unique=True, label=T('Client Name')),
                Field('active', 'boolean', default=True),
                format='%(name)s'
                )

db.define_table('matter',
                Field('client', db.client, readable=False, writable=False),
                Field('name', required=True, label=T('Matter Name')),
                Field('active', 'boolean', default=True),
                format='%(name)s'
                )

db.define_table('segment',
                Field('matter', db.matter, readable=False, writable=False),
                Field('name', required=True, label=T('Segment Name')),
                Field('active', 'boolean', default=True),
                format='%(name)s'
                )
db.define_table('time_entry',
                Field('client', db.client, length=150, requires=IS_IN_DB(db(db.client.active==True), db.client.id, '%(name)s')),
                Field('matter', db.matter, requires=IS_IN_DB(db(db.matter.active==True), db.matter.id, '%(name)s')),
                Field('segment', db.segment, requires=IS_EMPTY_OR(IS_IN_DB(db(db.segment.active==True),db.segment.id, '%(name)s'))),
                Field('fee_earner', db.auth_user, default=(session.fee_earner or auth.user_id),
                      requires=IS_IN_DB(db(db.auth_user.id.belongs(current_user_perm.auth_list) if current_user_perm else db.auth_user.id == auth.user_id), db.auth_user.id, '%(first_name)s %(last_name)s')),
                Field('code_classification',
                      requires=IS_IN_SET([T('Other'), T('Meeting'), T('Discussion'), T('Telephone Call'), T('Review/Analyse'), T('Draft/Revise'), T('Legal Research'), T('Travel')], zero=None), default='Other'),
                Field('description', 'text', required=True, represent=lambda d:MARKMIN(d.strip('"'))),
                Field('special_notes', 'text', represent=lambda sn:MARKMIN(sn.strip('"'))),
                Field('related_disbursements', 'list:string',
                      requires=IS_IN_SET([T('Mobile'), T('Telephone'), T('Travel'), T('Meals'), T('Other')], multiple=True)),
                Field('date', 'date'),
                Field('duration', 'double', requires=Float_validator()),
                #Field('cost',compute=cost),
                Field('rate', 'double'),
                Field('billable', 'boolean', default=True),
                Field('billed', 'boolean', default=False),
                auth.signature,
                format='%(description)s'
                )                

active_clients = db.client.active == True
active_matters = db.matter.active == True
active_segments = db.segment.active == True
a0,a1 = request.args(0), request.args(1)
total_duration = db.time_entry.duration.sum()
earner_entries = db.time_entry.fee_earner == db.auth_user.id
client_entries = db.time_entry.client == db.client.id
matter_entries = db.time_entry.matter == db.matter.id
segment_entries = db.time_entry.segment == db.segment.id
