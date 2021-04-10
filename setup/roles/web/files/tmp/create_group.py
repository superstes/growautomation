from sys import argv as sys_argv
import django
django.setup()

from django.contrib.auth.models import Group

group = sys_argv[1]

new_group, created = Group.objects.get_or_create(name=group)
new_group.save()
