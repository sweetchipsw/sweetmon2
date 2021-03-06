from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.dispatch import receiver
from datetime import datetime
from django.utils.timezone import now
import os
import hashlib
import base64
import time
import random
import string

crash_storage = FileSystemStorage(location=settings.CRASH_STORAGE_ROOT)
user_storage = FileSystemStorage(location=settings.USER_STORAGE_ROOT)


def get_upload_path(instance, filename):
    return '{0}/{1}'.format(instance.owner, filename)


def get_storage_path(instance, filename):
    return '{0}/{1}'.format(instance.owner, filename)


def generate_api_key():
    random.seed(str(time.time()))
    base = str(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(1024))).encode('utf-8')
    key = hashlib.sha256(base).hexdigest()
    return key


class Fuzzer(models.Model):
    owner = models.ForeignKey(User, on_delete=None)

    name = models.CharField(max_length=32, null=True, blank=True)
    target = models.CharField(max_length=256, null=True, blank=True)
    description = models.CharField(max_length=1024, null=True, blank=True)
    crash_cnt = models.IntegerField(default=0, blank=True, null=True)

    public_ip = models.CharField(max_length=16, blank=True)
    private_ip = models.CharField(max_length=16, blank=True)

    reg_date = models.DateTimeField(default=now, blank=True)
    ping_date = models.DateTimeField(default=now, blank=True)
    report_date = models.DateTimeField(default=now, blank=True)

    api_key = models.CharField(max_length=256, default=generate_api_key, help_text="", null=True, blank=True)

    def __str__(obj):
        return "%s" % (obj.name)


class Crash(models.Model):
    def __init__(self, *args, **kwargs):
        super(Crash, self).__init__(*args, **kwargs)

    owner = models.ForeignKey(User, on_delete=None)
    fuzzer = models.ForeignKey(Fuzzer, on_delete=None)
    parent_idx = models.IntegerField(default=0)

    title = models.CharField(max_length=1024)
    favorite = models.BooleanField(default=False)
    title_hash = models.CharField(max_length=256)
    file_hash = models.CharField(max_length=256)
    dup_crash_cnt = models.IntegerField(default=0)

    crash_log = models.TextField()

    is_dup_crash = models.BooleanField(default=False)
    crash_file = models.FileField(storage=crash_storage, upload_to=get_upload_path)

    reg_date = models.DateTimeField(default=now, blank=True)
    latest_date = models.DateTimeField(auto_now=True)

    comment = models.TextField(null=True, blank=True, default="")

    def __str__(obj):
        return "%s" % (obj.title)


class Storage(models.Model):
    owner = models.ForeignKey(User, on_delete=None)
    title = models.CharField(max_length=1024)
    hash = models.CharField(max_length=256)
    file = models.FileField(storage=user_storage, upload_to=get_upload_path)
    original_name = models.CharField(max_length=256)
    reg_date = models.DateTimeField(default=now, blank=True)
    download_count = models.IntegerField(default=0)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return "%s" % (self.title)

    def get_filename(self):
        if len(self.file.name.split('/')) > 0:
            return self.file.name.split('/')[-1]
        else:
            return self.file.name


class OnetimeUrl(models.Model):
    owner = models.ForeignKey(User, on_delete=None)
    token = models.CharField(max_length=256, default=generate_api_key)
    file = models.FileField(storage=crash_storage)
    is_expired = models.BooleanField(default=False)
    type = models.CharField(max_length=256, default="")
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=None)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(obj):
        return "%s" % (obj.file.name)


@receiver(pre_save, sender=Storage)
def my_callback(sender, instance, *args, **kwargs):
    instance.original_name = ""
    instance.hash = hashlib.sha256(instance.file.read()).hexdigest()