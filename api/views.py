from django.shortcuts import render
from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.http import Http404
import hashlib
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.utils.crypto import get_random_string
from django.conf import settings
from django.views.decorators.http import require_http_methods


def apikey_required_operator(request):
    # Raise http404 exception if api key is not exists in HTTP header.
    if "apikey" not in request.POST:
        raise Http404


def apikey_required(operation):
    def wrapper(*args, **kwargs):
        request = args[0]
        return apikey_required_operator(request)
    return wrapper


@apikey_required
@require_http_methods(["GET"])
def crash_download(request):
    return HttpResponse("Hello world Test1")


@apikey_required
@require_http_methods(["POST"])
def crash_generate_url(request):
    return HttpResponse("Hello world Test1")


@apikey_required
@require_http_methods(["POST"])
def crash_upload(request):
    return HttpResponse("Hello world Test1")


@apikey_required
@require_http_methods(["GET"])
def fuzzer_update_info(request):
    return HttpResponse("Hello world Test1")

@apikey_required
@require_http_methods(["GET"])
def fuzzer_ping(request):
    return HttpResponse("Hello world Test1")


@apikey_required
@require_http_methods(["GET"])
def storage_list(request):
    return HttpResponse("Hello world Test1")


@apikey_required
@require_http_methods(["GET"])
def storage_download(request):
    return HttpResponse("Hello world Test1")


@apikey_required
@require_http_methods(["GET"])
def health(request):
    result = {"result":True}
    return JsonResponse(result)