#started like this: python web2py.py -S [APPLICATION] -M -R applications/mcsa/modules/create_users.py
pwd1 = raw_input('Root password: ')
pwd2 = raw_input('Admin password: ')
u1 = auth.get_or_create_user({'first_name':'root', 'last_name':'root','email':'root@root.ro','password':db.auth_user.password.validate(pwd1)[0]})
u2 = auth.get_or_create_user({'first_name':'admin', 'last_name':'admin','email':'admin@admin.ro','password':db.auth_user.password.validate(pwd2)[0]})
g1 = db.auth_group(role='admin') or auth.add_group('admin', 'Administrator')
auth.add_membership(g1.id, u1.id)
auth.add_membership(g1.id, u2.id)
db.commit()
