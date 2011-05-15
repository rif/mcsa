# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = request.application
response.subtitle = T('Time tracker  application')

#http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Vox Filemaker Solutions'
response.meta.description = 'Time tracker application speccialy adapted to lawyers'
response.meta.keywords = 'time, tracker, timetracker, reports, clients, matters, segments, lawyers'
response.meta.generator = 'Web2py Enterprise Framework'
response.meta.copyright = 'Copyright 2011'


##########################################
## this is the main application menu
## add/remove items as required
##########################################

response.menu = [
    (T('Home'), False, URL('default','index'), []),
    (T('Clients'), False, URL('default', 'clients'), []),
    (T('Reports'), False, URL('default', 'reports'), [])
    ]
