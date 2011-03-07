# -*- coding: utf-8 -*-

def index():
    entries = db(db.time_entry.id>0).select()
    return dict(entries=entries)

def clients():
    clients = db(db.client.id>0).select()
    return dict(clients=clients)

def client_edit():
    client = None
    matters = None
    if len(request.args) > 0:
        client = db.client(request.args[0])
        matters = db(db.matter.client==client).select()
        form=crud.update(db.client, client, next=URL('clients'))
    else:
        form = crud.create(db.client, next=URL('clients'))
    return dict(form=form, client=client, matters=matters)

def matter_edit():
    matter = None
    client = db.client(request.args[0])
    db.matter.client.default = client
    if len(request.args) > 1:
        matter = db.matter(request.args[0])
        form=crud.update(db.matter, matter)
    else:
        form = crud.create(db.matter)
    return dict(form=form, matter=matter, client=client)

def entry_edit():
    entry = None
    if len(request.args) > 0:
        entry = db.time_entry(request.args[0])
        form=crud.update(db.time_entry, entry, next=URL('index'))
    else:
        form = crud.create(db.time_entry, next=URL('index'))
    return dict(form=form, entry=entry)

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
