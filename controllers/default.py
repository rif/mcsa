# -*- coding: utf-8 -*-

def index():
    entries = db(db.time_entry).select()
    return locals()

@auth.requires_membership('admin')
def clients():
    clients = db(db.client).select()
    return locals()

@auth.requires_membership('admin')
def client_delete():
    client = db(db.client.id==request.args[0]) or redirect(URL('clients'))
    client.delete()
    return ''

def __edit(request, odb, edit_link, delete_link):
    if len(request.args) > 0:
        client = odb(request.args[0])
        form=crud.update(odb, client, deletable=False)
    else:
        form = crud.create(odb)
    if form.accepts(request.vars):
        return SPAN(SPAN(A(form.vars.name, _href=URL(edit_link, args=form.vars.id), cid='cl_' + str(form.vars.id))),
                    SPAN(form.vars.billable),
                    SPAN(A('x', _onclick="$(this).parents('li').remove();$.get($(this).attr('href')); return false;", _href=URL(delete_link, args=form.vars.id))))
    return response.render('default/form.html', locals())


@auth.requires_membership('admin')
def client_edit():
    return __edit(request, db.client, 'client_edit', 'client_delete')

@auth.requires_membership('admin')
def matter_edit():
    if len(request.args) > 0:
        matter = db.matter(request.args[0])
        form=crud.update(db.matter, matter, deletable=False)
    else:
        form=crud.create(db.matter)
    if form.accepts(request.vars):
        return SPAN(SPAN(A(form.vars.name, _href=URL('matter_edit', args=form.vars.id), cid='mt_' + str(form.vars.id))),
                    SPAN(A('x', _onclick="$(this).parents('li').remove();$.get($(this).attr('href')); return false;", _href=URL('matter_delete', args=form.vars.id))))
    return response.render('default/form.html', locals())

@auth.requires_membership('admin')
def matter_delete():
    matter = db(db.matter.id==request.args[0]) or redirect(URL('clients'))
    matter.delete()
    return ''

@auth.requires_membership('admin')
def segment_edit():
    if len(request.args) > 0:
        segment = db.segment(request.args[0])
        form=crud.update(db.segment, segment, deletable=False)
    else:
        form=crud.create(db.segment)
    if form.accepts(request.vars):
        return SPAN(SPAN(A(form.vars.name, _href=URL('segment_edit', args=form.vars.id), cid='mt_' + str(form.vars.id))),
                    SPAN(A('x', _onclick="$(this).parents('li').remove();$.get($(this).attr('href')); return false;", _href=URL('segment_delete', args=form.vars.id))))
    return response.render('default/form.html', locals())

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
