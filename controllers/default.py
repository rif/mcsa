# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
from gluon.contrib import simplejson

@auth.requires_login()
def index():
    if session.fee_earner == None:
        session.fee_earner = auth.user_id
    if current_user_perm and len(current_user_perm.auth_list):
        form = SQLFORM.factory(
            Field('fee_earner', default=(request.vars.fee_earner or session.fee_earner or auth.user_id),
                  requires=IS_IN_DB(db(db.auth_user.id.belongs(current_user_perm.auth_list)), db.auth_user.id, '%(first_name)s %(last_name)s')),
            )
        if form.accepts(request.vars, session):
            response.flash = T('Fee earner changed to %s') % db.auth_user(form.vars.fee_earner).first_name
            session.fee_earner = form.vars.fee_earner
    return locals()

@auth.requires_membership('admin')
def clients():
    clients = db(db.client).select(orderby=db.client.name)
    return locals()

@auth.requires_membership('admin')
def client_edit():
    form = crud.update(db.client, a0, deletable=False)
    if form.accepts(request.vars, session):
        return A(form.vars.name, _class="show-link", _href=URL('matters', args=form.vars.id))
    return response.render('default/form.html', locals())

def client_new():
    form = crud.create(db.client)
    if form.accepts(request.vars, session):
        return """
<li>
  <a href="/mcsa/default/matters/%(id)s" class="show-link">%(name)s</a>
  <a href="/mcsa/default/client_edit/%(id)s" class="undercover edit-link">%(edit)s</a>
  <a href="/mcsa/default/client_delete/%(id)s" class="undercover delete-link"">%(del)s</a>
  <ul class="undercover">
     <a href="/mcsa/default/matter_new/%(id)s" class="edit-link">%(new)s</a>	
  </ul>
</li>
""" % {"name":form.vars.name, "id":form.vars.id, "edit":T('Edit'), "new":T('New matter'), "del":T('Delete')}
    return response.render('default/form.html', locals())


@auth.requires_membership('admin')
def matter_edit():
    form = crud.update(db.matter, a0, deletable=False)
    if form.accepts(request.vars, session):
        return A(form.vars.name)
    return response.render('default/form.html', locals())

@auth.requires_membership('admin')
def matter_new():
    db.matter.client.default = a0
    form = crud.create(db.matter)
    if form.accepts(request.vars, session):
        return """
<li>
  <a href="/mcsa/default/segments/%(id)s" class="show-link">%(name)s</a>
  <a href="/mcsa/default/matter_edit/%(id)s" class="undercover edit-link">%(edit)s</a>
  <a href="/mcsa/default/matter_delete/%(id)s" class="undercover delete-link"">%(del)s</a>
  <ul class="undercover">
     <a href="/mcsa/default/segment_new/%(id)s" class="edit-link">%(new)s</a>	
  </ul>
</li>
""" % {"name":form.vars.name, "id":form.vars.id, "edit":T('Edit'), "new":T('New segment'), "del":T('Delete')}
    return response.render('default/form.html', locals())

@auth.requires_membership('admin')
def segment_edit():
    form = crud.update(db.segment, a0, deletable=False)
    if form.accepts(request.vars, session):
        return A(form.vars.name, _class="show-link", _href=URL('matters', args=form.vars.id))
    return response.render('default/form.html', locals())


@auth.requires_membership('admin')
def segment_new():
    db.segment.matter.default = a0
    form = crud.create(db.segment)
    if form.accepts(request.vars, session):
        return """
<li>
  <a>%(name)s</a>
  <a href="/mcsa/default/segment_edit/%(id)s" class="undercover edit-link">%(edit)s</a>
  <a href="/mcsa/default/segment_delete/%(id)s" class="undercover delete-link"">%(del)s</a>
</li>
""" % {"name":form.vars.name, "id":form.vars.id, "edit":T('Edit'), "del":T('Delete')}


    return response.render('default/form.html', locals())

@auth.requires_membership('admin')
def client_delete():
    db(db.client.id==a0).delete()
    return ""

@auth.requires_membership('admin')
def matter_delete():
    db(db.matter.id==a0).delete()
    return ""

@auth.requires_membership('admin')
def segment_delete():
    db(db.segment.id==a0).delete()
    return ""

def _strip(form):
    form.vars.description = form.vars.description.strip()
    form.vars.special_notes = form.vars.special_notes.strip()

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
    form = crud.create(db.time_entry, next=URL('index'), onvalidation=_strip)
    return response.render('default/entry_edit.html', locals())

@auth.requires_login()
def entry_drop():
    entry = db.time_entry(a0)
    entry.update_record(date=datetime.fromtimestamp(float(a1)))
    return ''

def entry_edit():
    entry = None
    fee_earner = db.auth_user(session.fee_earner or auth.user_id)
    if a0 > 0:
        entry = db.time_entry(a0)
        fee_earner = entry.fee_earner or fee_earner
        #the requirements bellow do not work beacause it will not allow to change clients
        #db.time_entry.matter.requires=IS_IN_DB(db(db.matter.client==entry.client),db.matter.id, '%(name)s')
        #db.time_entry.segment.requires=IS_EMPTY_OR(IS_IN_DB(db(db.segment.matter==entry.matter),db.segment.id, '%(name)s'))
        form=crud.update(db.time_entry, entry, next=URL('index'), onvalidation=_strip)
    else:
        form = crud.create(db.time_entry, next=URL('index'), onvalidation=_strip)
    return locals()

@auth.requires_login()
def entries():
    start = datetime.fromtimestamp(float(request.vars.start))
    end = datetime.fromtimestamp(float(request.vars.end))
    if abs((start - end).days) > 7:
        session.current_date = (start+timedelta(15)).isoformat()
    else:
        session.current_date = start.isoformat()
    teset = db((db.time_entry.date >= start) & (db.time_entry.date <= end) & (db.time_entry.fee_earner == (session.fee_earner or auth.user_id)))
    sumus = db.time_entry.duration.sum()
    sum_select = teset.select(db.time_entry.date, sumus, groupby=db.time_entry.date)
    ent = []
    date_index = None
    for row in teset.select(orderby=db.time_entry.date):
        ent.append({'id': row.id,
            'title': str(row.duration) + ' ' + T('hours'),
            'description': row.description,
            'start': row.date.strftime("%Y-%m-%d"),
            'url': URL('entry_edit', args=row.id)})
        if date_index != row.date:
            date_index = row.date
            ent.append({'id':0,
                        'title': T('Total:%(total).1f hours') % {'total':sum_select.find(lambda r: r.time_entry.date==row.date).first()[sumus]},
                        'start': row.date.strftime("%Y-%m-%d") + " 23:59",
                        'description': T('Total for ') +  row.date.strftime("%Y-%m-%d"),
                        'backgroundColor': '#6699CC'})
        
    return simplejson.dumps(ent)

def change_view():
    session.view = a0

@auth.requires_login()
def matters_callback():
    client = db.client(a0)
    matters = db(active_matters & (db.matter.client==client)).select()
    option_list = [OPTION('')]
    for mat in matters:
        option_list.append(OPTION(mat.name, _value=mat.id))
    return SELECT(*option_list, _id='time_entry_matter', _class='reference', _name='matter')

@auth.requires_login()
def segment_callback():
    matter = db.matter(a0)
    segments = db(active_segments & (db.segment.matter==matter)).select()
    option_list = [OPTION('')]
    for seg in segments:
        option_list.append(OPTION(seg.name, _value=seg.id))
    return SELECT(*option_list, _id='time_entry_segment', _class='reference', _name='segment')

@auth.requires_login()
def reports():
    query = earner_entries & client_entries & matter_entries
    today = date.today()
    first_of_month = today.replace(day=1)
    form = SQLFORM.factory(
        Field('fee_earner', db.auth_user, requires=IS_EMPTY_OR(IS_IN_DB(db(db.auth_user.id>1), db.auth_user.id, '%(first_name)s %(last_name)s', zero=T('ALL'))), label=T('Fee earner')),
        Field('client', db.client, requires=IS_EMPTY_OR(IS_IN_DB(db(db.client), db.client.id,  '%(name)s', zero=T('ALL'))), label=T('Client')),
        Field('matter', db.matter, requires=IS_EMPTY_OR(IS_IN_DB(db(db.matter), db.matter.id, '%(name)s', zero=T('ALL'))), label=T('Matter')),
        Field('segment', db.segment, requires=IS_EMPTY_OR(IS_IN_DB(db(db.segment), db.segment.id, '%(name)s', zero=T('ALL'))), label=T('Segment')),
        Field('related_disbursements', 'list:string', requires=IS_IN_SET([T('Mobile'), T('Telephone'), T('Travel'), T('Meals'), T('Other')], multiple=True), label=T('Related disbursements')),
        Field('start', 'date', label=T('Start')),#, default=first_of_month),
        Field('end', 'date', label=T('End')),#, default=today)
        Field('csv', 'boolean', label=T('Download as CSV')),
        Field('pdf', 'boolean', label=T('Download as PDF')),
        )
    if form.accepts(request.vars, session):
        if form.vars.fee_earner: query &= db.time_entry.fee_earner == form.vars.fee_earner 
        if form.vars.client: query &= db.time_entry.client == form.vars.client
        if form.vars.matter: query &= db.time_entry.matter == form.vars.matter
        if form.vars.segment: query &= db.time_entry.segment == form.vars.segment
        if form.vars.related_disbursements:
            subquery = db.time_entry.related_disbursements.contains(form.vars.related_disbursements[0])
            for disbursement in form.vars.related_disbursements[1:]:
                subquery |= db.time_entry.related_disbursements.contains(disbursement)
            query &= subquery
        if form.vars.start: query &=  db.time_entry.date >= form.vars.start
        if form.vars.end: query &= db.time_entry.date <= form.vars.end
    elif form.errors:
        response.flash = 'form has errors'
    entries_set = db(query)
    entries = entries_set.select(db.auth_user.first_name, db.auth_user.last_name, db.client.name, db.matter.name, db.time_entry.date, db.time_entry.description, db.time_entry.special_notes, db.time_entry.duration, orderby=db.time_entry.date)
    powerTable = plugins.powerTable
    powerTable.datasource = entries
    powerTable.uitheme = 'redmond'
    powerTable.headers = 'labels'
    powerTable.dtfeatures['sScrollY'] = '600px'
    table = powerTable.create()
    earners = entries_set.select(db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, total_duration, orderby=~total_duration, groupby=db.auth_user.first_name)
    earner_names = [str(row.auth_user.id) for row in earners]
    earner_durations = [int(row[total_duration]) for row in earners]

    clients = entries_set.select(db.client.id, db.client.name, total_duration, orderby=~total_duration, groupby=db.client.name)
    client_names = [str(row.client.id) for row in clients]
    client_durations = [int(row[total_duration]) for row in clients]

    matters = entries_set.select(db.matter.id, db.matter.name, total_duration, orderby=~total_duration, groupby=db.matter.name)
    matter_names = [str(row.matter.id) for row in matters]
    matter_durations = [int(row[total_duration]) for row in matters]
    if form.vars.csv:
        response.headers['Content-Type']='application/excel'
        response.headers['Content-Disposition']='attachment'
        return response.render('generic.csv',locals())

    if form.vars.pdf:
        from gluon.contrib.pyfpdf import FPDF, HTMLMixin

        # define our FPDF class (move to modules if it is reused  frequently)
        class MyFPDF(FPDF, HTMLMixin):
            def header(self):
                self.set_font('Arial','B',15)
                self.cell(0,10, request.application + ' ' + T('time entries report') ,1,0,'C')
                self.ln(20)
                
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial','I',8)
                txt = 'Page %s of %s' % (self.page_no(), self.alias_nb_pages())
                self.cell(0,10,txt,0,0,'C')
                    
        pdf=MyFPDF('P', 'mm', 'A4')
        # first page:
        pdf.add_page()
        pdf.set_font('Arial','',8)
        pdf.write_html(response.render("default/pdf_reports.html", locals()))
        response.headers['Content-Type']='application/pdf'
        response.headers['Content-Disposition']='attachment'
        return pdf.output(dest='S')
    return locals()

@auth.requires_membership('admin')
def users():
    form = crud.update(db.auth_user, a0, next=URL('users'))
    users = db(db.auth_user).select()
    return locals()

@auth.requires_membership('admin')
def perm():
    p = db.perm(db.perm.user == a0)
    db.perm.user.default = a0
    form = crud.update(db.perm, p)
    return dict(form=form)

def force_language():
    session._lang = a0
    return redirect(request.env.http_referer)

def user():
    return dict(form=auth())
