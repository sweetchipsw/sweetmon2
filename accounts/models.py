from django.db.models.signals import pre_save, post_save
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User, Permission
from django.conf import settings
from django.db import models
import hashlib
import os

image_storage = FileSystemStorage(location=settings.IMAGE_STORAGE_ROOT)


def get_sha256_string(plain, convtohex=True):
    h = hashlib.sha256(plain)
    if convtohex:
        h = h.hexdigest()
    else:
        h = h.digest()
    return h


def get_image_upload_path(instance, filename):
    rd_str = get_sha256_string(str(os.urandom(32)).encode('utf-8'))
    rd_str_len = int(len(rd_str) / 2)
    location = '{0}/{1}.jpg'.format((rd_str[:rd_str_len]), (rd_str[rd_str_len:]))
    return location


class Profile(models.Model):
    owner = models.ForeignKey(User, on_delete=None)

    first_name = models.CharField(max_length=32, default="")
    last_name = models.CharField(max_length=32, default="")
    email = models.EmailField(max_length=256, default="")

    use_user_api = models.BooleanField(default=False, help_text="Enable to use user api.")
    api_key = models.CharField(max_length=64, default="", help_text="This key will required to use user api."
                                                                    "DO NOT SHARE THIS KEY.")

    # telegram_userid = models.CharField(max_length=32, blank=True)
    # use_telegram_alert = models.BooleanField(default=False,
    #                                          help_text="Use this feature if you want to subscribe crash.")
    # use_email_alert = models.BooleanField(default=False)
    # profile_image = models.FileField(storage=image_storage, null=True, blank=True, upload_to=get_image_upload_path)

    def __str__(obj):
        return "%s" % (obj.owner)


def create_profile(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        # Create user
        user_profile = Profile(owner=user)
        user_profile.email = user.email
        user_profile.last_name = user.last_name
        user_profile.first_name = user.first_name
        user_profile.api_key = get_sha256_string(str(os.urandom(32)).encode('utf-8'))
        user_profile.save()

        # Allow access to admin page
        user = User.objects.get(id=user.id)
        user.is_staff = True;

        """
        'Can add fuzzer', 'Can change fuzzer', 'Can delete fuzzer',
        'Can add storage', 'Can change storage', 'Can delete storage',
        """
        # Add permissions for staff
        permission_list = ['Can add fuzzer', 'Can change fuzzer', 'Can delete fuzzer', 'Can add storage',
                           'Can change storage', 'Can delete storage', 'Can change profile']
        for permission in permission_list:
            userperm = Permission.objects.get(name=permission)
            user.user_permissions.add(userperm)
        user.save()


def SyncUserProfile(sender, **kwargs):
    # Gen userkey
    # BUG :  NOT NULL constraint failed: accounts_profile.first_name
    profile = kwargs["instance"]
    if not kwargs["created"]:
        user_profile = User.objects.get(id=profile.owner.id)
        if profile.email != "":
            user_profile.email = profile.email
        if profile.last_name != "":
            user_profile.last_name = profile.last_name
        if profile.first_name != "":
            user_profile.first_name = profile.first_name
        user_profile.save()


post_save.connect(create_profile, sender=User)
post_save.connect(SyncUserProfile, sender=Profile)

"""
# TODO : Impl alertbot
class AlertBot(models.Model):
    owner = models.ForeignKey(User, on_delete=None)
    title = models.CharField(max_length=1024)
"""
