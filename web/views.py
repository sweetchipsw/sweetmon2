from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.http import Http404
import hashlib
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.utils.crypto import get_random_string
from django.conf import settings
from django.contrib.auth.decorators import login_required


def test(request):
    return HttpResponse("Hello world Test accoun t")


def index(request):
    context = {}
    return render(request, 'web/index.html', context)


def fuzzer(request):
    context = {}
    return render(request, 'web/fuzzer.html', context)


def fuzzer_detail(request, idx):
    context = {}
    return render(request, 'web/fuzzer_detail.html', context)


def crash(request):
    context = {}
    return render(request, 'web/crash.html', context)


def crash_detail(request, idx):
    context = {}
    return render(request, 'web/crash_detail.html', context)


def api_docs(request):
    context = {}
    return render(request, 'web/api_docs.html', context)


def sweetmon_client(request):
    context = {}
    return render(request, 'web/sweetmon_client.html', context)


def storage(request):
    context = {}
    return render(request, 'web/storage.html', context)


def storage_detail(request, idx):
    context = {}
    return render(request, 'web/storage_detail.html', context)


def error_not_found(request):
    return render(request, 'common/404.html')


def error_internal_error(request):
    return render(request, 'common/500.html')
