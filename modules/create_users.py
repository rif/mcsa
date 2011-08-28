u1 = auth.get_or_create_user({'first_name':'root', 'last_name':'root','email':'root@root.ro','password':'testus_cumulus'})
u2 = auth.get_or_create_user({'first_name':'admin', 'last_name':'admin','email':'admin@admin.ro','password':'testus_cumulus'})
g1 = db.auth_group(role='admin') or auth.add_group('admin', 'Administrator')
auth.add_membership(g1.id, u1.id)
auth.add_membership(g1.id, u2.id)
db.commit()
