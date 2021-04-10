from sys import argv as sys_argv
import django
django.setup()

from django.contrib.auth.models import User, Group

name = sys_argv[1]
secret = sys_argv[2]
domain = sys_argv[3]
groups = sys_argv[4].split(',')

try:
    su = int(sys_argv[5])

except (IndexError, TypeError):
    su = 0

try:
    user = User.objects.create_user(username=name, email=f'{name}@{domain}', password=secret)

except django.db.utils.IntegrityError:
    user = User.objects.get(username=name)

if su == 1:
    user.is_superuser = True
    user.is_staff = True

else:
    user.is_superuser = False
    user.is_staff = False

for group in groups:
    grp_obj = Group.objects.get(name=group)
    user.groups.add(grp_obj)

user.save()


