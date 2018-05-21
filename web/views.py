from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.http import Http404
import hashlib
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.utils.crypto import get_random_string
from django.conf import settings
from django.contrib.auth.decorators import login_required
from api.models import Fuzzer, Crash, Storage
from django.contrib.auth.models import User


def index(request):
    try:
        fuzzer = Fuzzer.objects.all()
        crash = Crash.objects.all()
        storage = Storage.objects.all()
        user = User.objects.all()
    except ObjectDoesNotExist:
        raise Http404

    context = {'crash': crash, 'fuzzer': fuzzer, 'storage': storage, 'user': user}
    return render(request, 'web/index.html', context)


def fuzzer(request):
    try:
        fuzzer = Fuzzer.objects.all()
    except ObjectDoesNotExist:
        raise Http404
    context = {'fuzzer_list':fuzzer}
    return render(request, 'web/fuzzer.html', context)


def fuzzer_detail(request, idx):
    try:
        fuzzer = Fuzzer.objects.get(id=idx)
    except ObjectDoesNotExist:
        raise Http404
    context = {'fuzzer':fuzzer}
    return render(request, 'web/fuzzer_detail.html', context)


def crash(request):
    try:
        crash = Crash.objects.all()
    except ObjectDoesNotExist:
        raise Http404
    context = {'crash_list':crash}
    return render(request, 'web/crash.html', context)


def crash_detail(request, idx):
    try:
        crash = Crash.objects.get(id=idx)
    except ObjectDoesNotExist:
        raise Http404
    context = {'crash':crash}
    return render(request, 'web/crash_detail.html', context)


def storage(request):
    try:
        storage = Storage.objects.all()
    except ObjectDoesNotExist:
        raise Http404
    context = {'storage_list':storage}
    return render(request, 'web/storage.html', context)


def storage_detail(request, idx):
    try:
        storage = Storage.objects.get(id=idx)
    except ObjectDoesNotExist:
        raise Http404
    context = {'storage':storage}
    return render(request, 'web/storage_detail.html', context)


def api_docs(request):
    context = {}
    return render(request, 'web/api_docs.html', context)


def sweetmon_client(request):
    context = {}
    return render(request, 'web/sweetmon_client.html', context)


def error_not_found(request):
    return render(request, 'common/404.html')


def error_internal_error(request):
    return render(request, 'common/500.html')
