from .config.shared import GA_USER_GROUP, GA_READ_GROUP, GA_WRITE_GROUP


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
