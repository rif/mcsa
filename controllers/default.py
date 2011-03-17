# -*- coding: utf-8 -*-
import datetime
from gluon.contrib import simplejson

def index():
    entries = db(db.time_entry).select()
    return locals()

@auth.requires_membership('admin')
def clients():
    clients = db(db.client).select()
    return locals()

def __edit(request, odb, edit_link, sel):
    if len(request.args) > 0 and request.vars.new != 1:
        obj = odb(request.args[0])
        form=crud.update(odb, obj, deletable=False)
    else:
        form = crud.create(odb)
    if form.accepts(request.vars):
        return SPAN(
            SPAN(A(form.vars.name, _href=URL(edit_link, args=form.vars.id), cid=sel + str(form.vars.id))),
            ' ', 
            SPAN(form.vars.billable) if form.vars.billable else ' ',
            ' ', _id=form.vars.id)
    return response.render('default/form.html', locals())

@auth.requires_membership('admin')
def new_template():
    eid = request.args[1]
    pairs = {
        'cl': (URL('data', args=('delete','client', eid)), 'New matter', 'matter_edit'),
        'mt': (URL('data', args=('delete','matter', eid)), 'New segment', 'segment_edit'),
        'sg': (URL('data', args=('delete','segment', eid)), None, None),
        }
    sel = {'cl': 'mt', 'mt': 'sg', 'sg': 'sg'}
    delete_link, new_string, new_link = pairs[request.args[0]]
    selector = sel[request.args[0]]
    return locals()

@auth.requires_membership('admin')
def client_edit():
    return __edit(request, db.client, 'client_edit', 'cl_')

@auth.requires_membership('admin')
def matter_edit():
    if request.vars.new == 'True':
        db.matter.client.default = db.client(request.args[0])    
    return __edit(request, db.matter, 'matter_edit', 'mt_')

@auth.requires_membership('admin')
def segment_edit():
    if request.vars.new == 'True':
        db.segment.matter.default = db.matter(request.args[0])    
    return __edit(request, db.segment, 'segment_edit', 'sg_')

def entry_new():
    entry = None
    user = None
    db.time_entry.date.default = datetime.datetime.fromtimestamp(float(request.args[0]))
    form = crud.create(db.time_entry, next=URL('index'))
    return response.render('default/entry_edit.html', locals())

def entry_edit():
    entry = None
    user = auth.user_id
    if len(request.args) > 0:
        entry = db.time_entry(request.args[0])
        user = db.auth_user(entry.created_by)
        #the requirements bellow do not work beacause it will not allow to change clients
        #db.time_entry.matter.requires=IS_IN_DB(db(db.matter.client==entry.client),db.matter.id, '%(name)s')
        #db.time_entry.segment.requires=IS_EMPTY_OR(IS_IN_DB(db(db.segment.matter==entry.matter),db.segment.id, '%(name)s'))
        form=crud.update(db.time_entry, entry, next=URL('index'))
    else:
        form = crud.create(db.time_entry, next=URL('index'))
    return locals()

def entries():
    start = datetime.datetime.fromtimestamp(float(request.vars.start))
    end = datetime.datetime.fromtimestamp(float(request.vars.end))
    ent = []
    for row in db((db.time_entry.date >= start) & (db.time_entry.date <= end)).select():
        ent.append({'id': row.id,
                    'title': row.description[:15] +"...",
                    'start': row.date.strftime("%Y-%m-%d"),
                    'url': URL('entry_edit', args=row.id).xml()})
    return simplejson.dumps(ent)

def matters_callback():
    client = db.client(request.args[0])
    matters = db(db.matter.client==client).select()
    option_list = [OPTION('')]
    for mat in matters:
        option_list.append(OPTION(mat.name, _value=mat.id))
    return SELECT(*option_list, _id='time_entry_matter', _class='reference', _name='matter')

def segment_callback():
    matter = db.matter(request.args[0])
    segments = db(db.segment.matter==matter).select()
    option_list = [OPTION('')]
    for seg in segments:
        option_list.append(OPTION(seg.name, _value=seg.id))
    return SELECT(*option_list, _id='time_entry_segment', _class='reference', _name='segment')

@auth.requires_membership('admin')
def data(): return dict(form=crud())


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()
