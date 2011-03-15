# -*- coding: utf-8 -*-

def index():
    entries = db(db.time_entry).select()
    return locals()

@auth.requires_membership('admin')
def clients():
    clients = db(db.client).select()
    return locals()

@auth.requires_membership('admin')
def client_new():
    form = crud.create(db.client, next=URL('clients'))
    return locals()

@auth.requires_membership('admin')
def client_delete():
    client = db(db.client.id==request.args[0]) or redirect(URL('clients'))
    client.delete()
    return ''

@auth.requires_membership('admin')
def client_edit():
    client = db.client(request.args[0])
    form=SQLFORM(db.client, client)
    if form.accepts(request.vars):
        return SPAN(SPAN(A(form.vars.name, _href=URL('client_edit1', args=client.id), cid='cl_' + str(client.id))),
                    SPAN(form.vars.billable),
                    SPAN(A('x', _onclick="$(this).parents('li').remove();$.get($(this).attr('href')); return false;", _href=URL('client_delete', args=client.id))))
    elif form.errors:
        response.flash = TABLE(*[TR(k, v) for k, v in form.errors.items()])
        return SPAN(SPAN(A(client.name, _href=URL('client_edit1', args=client.id), cid='cl_' + str(client.id))),
                    SPAN(client.billable),
                    SPAN(A('x', _onclick="$(this).parents('li').remove();$.get($(this).attr('href')); return false;", _href=URL('client_delete', args=client.id))))
    return locals()

        
@auth.requires_membership('admin')
def matter_new():
    form = crud.create(db.matter, next=URL('clients'), message=T('Matter created'))
    return locals()

@auth.requires_membership('admin')
def matter_edit1():
    matter = db.matter(request.args[0])
    form=SQLFORM(db.matter, matter)
    if form.accepts(request.vars):
        return SPAN(SPAN(A(form.vars.name, _href=URL('matter_edit1', args=matter.id), cid='mt_' + str(matter.id))),
                    SPAN(A('x', _onclick="$(this).parents('li').remove();$.get($(this).attr('href')); return false;", _href=URL('matter_delete', args=matter.id))))
    elif form.errors:
        response.flash = TABLE(*[TR(k, v) for k, v in form.errors.items()])
        return SPAN(SPAN(A(matter.name, _href=URL('matter_edit1', args=matter.id), cid='mt_' + str(matter.id))),
                    SPAN(A('x', _onclick="$(this).parents('li').remove();$.get($(this).attr('href')); return false;", _href=URL('matter_delete', args=matter.id))))
    return locals()

@auth.requires_membership('admin')
def matter_delete():
    matter = db(db.matter.id==request.args[0]) or redirect(URL('clients'))
    matter.delete()
    return ''

@auth.requires_membership('admin')
def segment_new():
    form = crud.create(db.segment, next=URL('clients'), message=T('Segment created'))
    return locals()

@auth.requires_membership('admin')
def segment_edit():
    segment = db.segment(request.args[0])
    form=SQLFORM(db.segment, segment)
    if form.accepts(request.vars):
        return SPAN(SPAN(A(form.vars.name, _href=URL('segment_edit1', args=segment.id), cid='mt_' + str(segment.id))),
                    SPAN(A('x', _onclick="$(this).parents('li').remove();$.get($(this).attr('href')); return false;", _href=URL('segment_delete', args=segment.id))))
    elif form.errors:
        response.flash = TABLE(*[TR(k, v) for k, v in form.errors.items()])
        return SPAN(SPAN(A(segment.name, _href=URL('segment_edit1', args=segment.id), cid='mt_' + str(segment.id))),
                    SPAN(A('x', _onclick="$(this).parents('li').remove();$.get($(this).attr('href')); return false;", _href=URL('segment_delete', args=segment.id))))
    return locals()

@auth.requires_membership('admin')
def segment_delete():
    segment = db(db.segment.id==request.args[0]) or redirect(URL('clients'))
    segment.delete()
    return ''

def entry_edit():
    entry = None
    user = None
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
