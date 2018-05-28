from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, User
from django.contrib.auth.models import Permission
from datetime import datetime
import os
import hashlib
import base64
import time
import random
import string

crash_storage = FileSystemStorage(location=settings.CRASH_STORAGE_ROOT)
user_storage = FileSystemStorage(location=settings.USER_STORAGE_ROOT)


def get_crash_path(instance, filename):
    return '{0}/{1}/{2}'.format(instance.owner.name, instance.crash_file.name, filename)


def get_user_upload_path(instance, filename):
    return '{0}/{1}'.format(instance.file.name, filename)


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

    reg_date = models.DateTimeField(default=datetime.now, blank=True)
    ping_date = models.DateTimeField(default=datetime.now, blank=True)

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
    crash_hash = models.CharField(max_length=256)
    dup_crash_cnt = models.IntegerField(default=0)

    crash_log = models.TextField()

    is_dup_crash = models.BooleanField(default=False)
    crash_file = models.FileField(storage=crash_storage)# , upload_to=get_crash_path)

    reg_date = models.DateTimeField(default=datetime.now, blank=True)
    latest_date = models.DateTimeField(auto_now=True)

    comment = models.TextField(null=True, blank=True)

    def __str__(obj):
        return "%s" % (obj.title)


class Storage(models.Model):
    owner = models.ForeignKey(User, on_delete=None)
    title = models.CharField(max_length=1024)
    hash = models.CharField(max_length=256)
    file = models.FileField(storage=user_storage, upload_to=get_user_upload_path)
    original_name = models.CharField(max_length=256)
    reg_date = models.DateTimeField(default=datetime.now, blank=True)
    download_count = models.IntegerField(default=0)
    comment = models.TextField(null=True, blank=True)

    def __str__(obj):
        return "%s" % (obj.title)


class OnetimeUrl(models.Model):
    owner = models.ForeignKey(User, on_delete=None)
    token = models.CharField(max_length=256, default=generate_api_key)
    file = models.FileField(storage=crash_storage)
    is_expired = models.BooleanField(default=False)


    def __str__(obj):
        return "%s" % (obj.file.name)
