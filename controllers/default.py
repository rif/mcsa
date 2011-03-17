# -*- coding: utf-8 -*-

def index():
    entries = db(db.time_entry).select()
    return locals()

@auth.requires_membership('admin')
def clients():
    clients = db(db.client).select()
    return locals()

def __edit(request, odb, edit_link):
    if len(request.args) > 0 and request.vars.new != 1:
        obj = odb(request.args[0])
        form=crud.update(odb, obj, deletable=False)
    else:
        form = crud.create(odb)
    if form.accepts(request.vars):
        return SPAN(
            SPAN(A(form.vars.name, _href=URL(edit_link, args=form.vars.id), cid='cl_' + str(form.vars.id))),
            ' ', 
            SPAN(form.vars.billable) if form.vars.billable else ' ',
            ' ', _id=form.vars.id)
    return response.render('default/form.html', locals())

def __delete(odb):
    obj = db(odb.id==request.args[0]) or redirect(URL('clients'))
    obj.delete()
    return ''

@auth.requires_membership('admin')
def new_template():
    pairs = {
        'cl': ('client_delete', 'New matter', 'matter_edit'),
        'mt': ('matter_delete', 'New segment', 'segment_edit'),
        'sg': ('segment_delete', None, None),
        }
    sel = {'cl': 'mt', 'mt': 'sg', 'sg': 'sg'}
    delete_link, new_string, new_link = pairs[request.args[0]]
    selector = sel[request.args[0]]
    eid = request.args[1]
    return locals()

@auth.requires_membership('admin')
def client_edit():
    return __edit(request, db.client, 'client_edit')

@auth.requires_membership('admin')
def client_delete():
    return __delete(db.client)

@auth.requires_membership('admin')
def matter_edit():
    if request.vars.new == 'True':
        db.matter.client.default = db.client(request.args[0])    
    return __edit(request, db.matter, 'matter_edit')

@auth.requires_membership('admin')
def matter_delete():
    return __delete(db.matter)

@auth.requires_membership('admin')
def segment_edit():
    if request.vars.new == 'True':
        db.segment.matter.default = db.matter(request.args[0])    
    return __edit(request, db.segment, 'segment_edit')

@auth.requires_membership('admin')
def segment_delete():
    return __delete(db.segment)

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
