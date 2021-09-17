from django.contrib.auth.models import User, Group
from .config.site import GA_USER_GROUP, GA_READ_GROUP, GA_WRITE_GROUP


def create(_):
    # Create ga groups
    group_list = [GA_READ_GROUP, GA_USER_GROUP, GA_WRITE_GROUP]

    for group in group_list:
        grp, created_grp = Group.objects.get_or_create(name=group)
        if created_grp:
            grp.save()

    # Create ga users
    user_dict = {
        'ga': {'pwd': '789TMP01', 'group_list': group_list},
        'demo': {'pwd': 'nice2020', 'group_list': [GA_USER_GROUP, GA_READ_GROUP]},
    }
    mail_domain = 'growautomation.local'

    for user, nested in user_dict.items():
        usr, created_user = User.objects.objects.get_or_create(username=user)
        if created_user:
            usr.set_password(nested['pwd'])
            usr.email(f"{user}@{mail_domain}")

            for grp in nested['group_list']:
                grp_obj = Group.objects.get(name=grp)
                usr.groups.add(grp_obj)

            usr.save()

    return f"{ User.objects.all() }"


def authorized_to_access(user):
    if user and user.groups.filter(name=GA_USER_GROUP).exists():
        return True

    return False


def authorized_to_read(user):
    if user and user.groups.filter(name=GA_READ_GROUP).exists():
        return True

    return False


def authorized_to_write(user):
    if user and user.groups.filter(name=GA_WRITE_GROUP).exists():
        return True

    return False
