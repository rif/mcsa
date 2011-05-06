# -*- coding: utf-8 -*-
from datetime import datetime, date
from gluon.contrib import simplejson

@auth.requires_login()
def index():
    if session.fee_earner == None:
        session.fee_earner = auth.user_id
    form = SQLFORM.factory(
        Field('fee_earner', default=(request.vars.fee_earner or session.fee_earner or auth.user_id),
              requires=IS_IN_DB(db(db.auth_user.id>1), db.auth_user.id, '%(first_name)s %(last_name)s')),
    )
    if form.accepts(request.vars, session):
        response.flash = T('Fee earner changed to %s') % db.auth_user(form.vars.fee_earner).first_name
        session.fee_earner = form.vars.fee_earner
    return locals()

@auth.requires_membership('admin')
def clients():
    clients = db(db.client).select()
    return locals()

def __edit(request, odb, edit_link, sel):
    if len(request.args) > 0 and request.vars.new != 'True':
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

@auth.requires_login()
def entry_new():
    entry = None
    user = None
    start = datetime.fromtimestamp(float(request.vars.start))
    end = datetime.fromtimestamp(float(request.vars.end))
    db.time_entry.date.default = start
    delta = end - start
    minutes = delta.days * 24 * 60 + delta.seconds / 60
    duration = minutes / 6 * 0.1
    db.time_entry.duration.default = duration
    form = crud.create(db.time_entry, next=URL('index'))
    return response.render('default/entry_edit.html', locals())

@auth.requires_login()
def entry_drop():
    entry = db.time_entry(request.args[0])
    entry.update_record(date=datetime.fromtimestamp(float(request.args[1])))
    return ''

def entry_edit():
    entry = None
    fee_earner = db.auth_user(session.fee_earner or auth.user_id)
    if len(request.args) > 0:
        entry = db.time_entry(request.args[0])
        fee_earner = entry.fee_earner or fee_earner
        #the requirements bellow do not work beacause it will not allow to change clients
        #db.time_entry.matter.requires=IS_IN_DB(db(db.matter.client==entry.client),db.matter.id, '%(name)s')
        #db.time_entry.segment.requires=IS_EMPTY_OR(IS_IN_DB(db(db.segment.matter==entry.matter),db.segment.id, '%(name)s'))
        form=crud.update(db.time_entry, entry, next=URL('index'))
    else:
        form = crud.create(db.time_entry, next=URL('index'))
    return locals()

def entries():
    start = datetime.fromtimestamp(float(request.vars.start))
    end = datetime.fromtimestamp(float(request.vars.end))
    ent = [{'id': row.id,
            'title': str(row.duration) + ' ' + T('hours'),
            'start': row.date.strftime("%Y-%m-%d"),
            'url': URL('entry_edit', args=row.id)}
           for row in db((db.time_entry.date >= start) &
                         (db.time_entry.date <= end) &
                         (db.time_entry.fee_earner == (session.fee_earner or auth.user_id))).select()]
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

@auth.requires_login()
def reports():
    response.title = T('Time entries report')
    if len(request.args): page=int(request.args[0])
    else: page=0
    items_per_page=20
    limitby=(page*items_per_page,(page+1)*items_per_page+1)
    if request.extension in ('csv', 'pdf'):
        limitby = 0
    query = earner_entries & client_entries & matter_entries
    entries_set = db(query = earner_entries & client_entries & matter_entries)
    today = date.today()
    first_of_month = today.replace(day=1)
    form = SQLFORM.factory(
        Field('fee_earner', db.auth_user, requires=IS_EMPTY_OR(IS_IN_DB(db(db.auth_user.id>1), db.auth_user.id, '%(first_name)s %(last_name)s', zero=T('ALL')))),
        Field('client', db.client, requires=IS_EMPTY_OR(IS_IN_DB(db(db.client), db.client.id,  '%(name)s', zero=T('ALL')))),
        Field('matter', db.matter, requires=IS_EMPTY_OR(IS_IN_DB(db(db.matter), db.matter.id, '%(name)s', zero=T('ALL')))),
        Field('start', 'date', default=first_of_month),
        Field('end', 'date', default=today))
    if form.accepts(request.vars, session, keepvalues=True):
        if form.vars.fee_earner: query &= db.time_entry.fee_earner == form.vars.fee_earner 
            
        if form.vars.client: query &= db.time_entry.client == form.vars.client
        if form.vars.matter: query &= db.time_entry.matter == form.vars.matter
        if form.vars.start: query &=  db.time_entry.date >= form.vars.start
        if form.vars.end: query &= db.time_entry.date <= form.vars.end
        entries_set = db(query)
        
    elif form.errors:
        response.flash = 'form has errors'
    entries = entries_set.select(db.auth_user.first_name, db.auth_user.last_name, db.client.name, db.matter.name, db.time_entry.date, db.time_entry.description, db.time_entry.duration, orderby=db.time_entry.date, limitby=limitby)
    earners = entries_set.select(db.auth_user.id, db.auth_user.first_name, total_duration, orderby=~total_duration, groupby=db.auth_user.first_name)
    earner_names = [str(row.auth_user.id) for row in earners]
    earner_durations = [int(row[total_duration]) for row in earners]

    clients = entries_set.select(db.client.id, db.client.name, total_duration, orderby=~total_duration, groupby=db.client.name)
    client_names = [str(row.client.id) for row in clients]
    client_durations = [int(row[total_duration]) for row in clients]

    matters = entries_set.select(db.matter.id, db.matter.name, total_duration, orderby=~total_duration, groupby=db.matter.name)
    matter_names = [str(row.matter.id) for row in matters]
    matter_durations = [int(row[total_duration]) for row in matters]
    if request.extension=="pdf":
        from gluon.contrib.pyfpdf import FPDF, HTMLMixin

        # define our FPDF class (move to modules if it is reused  frequently)
        class MyFPDF(FPDF, HTMLMixin):
            def header(self):
                self.set_font('Arial','B',15)
                self.cell(0,10, response.title ,1,0,'C')
                self.ln(20)
                
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial','I',8)
                txt = 'Page %s of %s' % (self.page_no(), self.alias_nb_pages())
                self.cell(0,10,txt,0,0,'C')
                    
        pdf=MyFPDF('L', 'mm', 'A4')
        # first page:
        pdf.add_page()
        pdf.set_font('Arial','',8)
        pdf.write_html(response.render("default/reports.pdf", locals()))
        response.headers['Content-Type']='application/pdf'
        return pdf.output(dest='S')
    return locals()


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
