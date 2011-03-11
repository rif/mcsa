# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

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
    db = DAL('sqlite://storage.sqlite')       # if not, use SQLite or other DB
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
mail.settings.sender = 'you@gmail.com'         # your email
mail.settings.login = 'username:password'      # your credentials or None

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

crud.settings.auth = None                      # =auth to enforce authorization on crud

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

db.define_table('client',
                Field('name', required=True, unique=True),
                Field('billable', 'boolean', default=True),
                format='%(name)s'
                )

db.define_table('matter',
                Field('client', db.client, readable=False, writable=False),
                Field('name', required=True),
                format='%(name)s'
                )

db.define_table('segment',
                Field('matter', db.matter, readable=False, writable=False),
                Field('name', required=True),
                format='%(name)s'
                )
                
db.define_table('time_entry',
                Field('client', db.client),
                Field('matter', db.matter),
                Field('segment', db.segment),
                Field('code_classification', requires=IS_IN_SET(['Other', 'Meeting', 'Discussion', 'Telephone Call', 'Review/Analyse', 'Draft/Revise', 'Legal Research', 'Travel'], zero=None), default='Other'),
                Field('user', db.auth_user, default=auth.user_id, update=auth.user_id, writable=False, readable=False),
                Field('description', 'text', required=True),
                Field('special_notes', 'text'),
                Field('related_disbursements', 'list:string', requires=IS_IN_SET(['Mobile', 'Telephone', 'Travel', 'Meals', 'Other'], multiple=True)),
                Field('date', 'date'),
                Field('duration', 'double', requires=IS_FLOAT_IN_RANGE(0.1,24)),
                #Field('cost',compute=cost),
                Field('rate', 'double'),
                Field('billable', 'boolean', default=True),
                Field('billed', 'boolean', default=False),
                Field('creation_time', 'datetime', readable=False, writable=False, default=request.now),
                format='%(description)s'
                )                
