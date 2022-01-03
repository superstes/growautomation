from sys import argv as sys_argv
import django
django.setup()

from django.contrib.auth.models import User

name = sys_argv[1]
secret = sys_argv[2]

user = User.objects.get(username=name)
user.set_password(secret)
user.save()
