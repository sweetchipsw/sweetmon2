from django.shortcuts import render, get_object_or_404
from django.utils.crypto import get_random_string
from django.conf import settings
from functools import wraps
from django.utils.decorators import decorator_from_middleware
from calendar import timegm
from django.http import HttpResponseNotAllowed
from django.utils.cache import get_conditional_response
from django.utils.http import http_date, quote_etag
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpResponseNotAllowed, FileResponse, Http404
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.utils.decorators import decorator_from_middleware
from django.middleware.http import ConditionalGetMiddleware
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import *
from api.models import Crash, Storage, Fuzzer, OnetimeUrl
from datetime import datetime
from functools import wraps
import hashlib

conditional_page = decorator_from_middleware(ConditionalGetMiddleware)


def apikey_required_do(stub):
    """
    Decorator to check 'api key' contains in HTTP Header.
    """
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            result = {"result": False, "message": None}
            if "HTTP_APIKEY" not in request.META:
                result['message'] = get_error_msg('wrong_apikey')
                return JsonResponse(result)
            return func(request, *args, **kwargs)
        return inner
    return decorator


apikey_required = apikey_required_do(["GET"])


def check_param(request_method, parameter):
    for param in parameter:
        if param not in request_method:
            return False
    return True


def get_apikey(request):
    return request.META['HTTP_APIKEY']


def get_error_msg(key):
    error_list = {"wrong_apikey": "Invalid API Key.",
                  "wrong_param": "Invalid parameter.",
                  "unknown": "Unknown error",
                  "expired_token": "Token expired."}
    return error_list[key]


@require_GET
@login_required
def crash_download(request, idx):
    result = {"result": False, "message": None}
    try:
        crash = Crash.objects.get(owner=request.user, id=idx)
    except ObjectDoesNotExist:
        crash = None

    if not crash:
        result['message'] = get_error_msg('wrong_param')
        return JsonResponse(result)

    f = crash.crash_file

    response = FileResponse(f.file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(f.name)

    return response


@require_GET
@login_required
def crash_generate_url(request, idx):
    result = {"result": False, "message": None}

    try:
        crash = Crash.objects.get(owner=request.user, id=idx)
    except ObjectDoesNotExist:
        crash = None

    if not crash:
        result['message'] = get_error_msg('wrong_param')
        return JsonResponse(result)

    f = crash.crash_file

    try:
        otu = OnetimeUrl.objects.get(owner=request.user, file=f, is_expired=False)
    except ObjectDoesNotExist:
        otu = None

    if not otu:
        otu = OnetimeUrl(owner=request.user, file=f, type="crash")
        otu.save()

    scheme = request.is_secure() and "https" or "http"
    result["result"] = True
    result["token"] = otu.token
    result["url"] = scheme + "://" + request.META['HTTP_HOST'] + "/api/v1/share/download?token=" + otu.token
    return JsonResponse(result)


@require_GET
@login_required
def crash_dup_crash_list(request, idx):
    result = {"result": False, "message": None}
    try:
        crash = Crash.objects.filter(owner=request.user, parent_idx=idx)
    except ObjectDoesNotExist:
        result['message'] = get_error_msg('wrong_param')
        return JsonResponse(result)

    paginator = Paginator(crash, 30)
    page = request.GET.get('p', 1)

    try:
        crash = paginator.page(page)
    except PageNotAnInteger:
        crash = paginator.page(1)
    except EmptyPage:
        crash = paginator.page(paginator.num_pages)

    if page not in paginator.page_range:
        paginator.page(1)

    index = paginator.page_range.index(crash.number)
    max_index = len(paginator.page_range)
    start_index = index - 5 if index >= 5 else 0
    end_index = index + 5 if index <= max_index - 5 else max_index
    page_range = paginator.page_range[start_index:end_index]

    crash_list = []
    for c in crash:
        temp = dict()
        crash_name = c.crash_file.name
        if "/" in crash_name:
            crash_name = crash_name.split("/")[-1]
        temp['name'] = crash_name
        temp['size'] = c.crash_file.size
        temp['date'] = c.reg_date
        temp['id'] = c.id
        crash_list.append(temp)

    result = {'result': True, "message": None, 'crashes': crash_list}

    return JsonResponse(result)


@require_GET
def file_download_by_otu(request):
    result = {"result": False, "message": None}

    param_list = ["token"]
    if not check_param(request.GET, param_list):
        result['message'] = get_error_msg('wrong_param')
        return JsonResponse(result)

    token = request.GET['token']

    if not token:
        result['message'] = get_error_msg('wrong_param')
        return JsonResponse(result)

    try:
        otu = OnetimeUrl.objects.get(token=token)
    except ObjectDoesNotExist:
        otu = None

    if not otu:
        result['message'] = get_error_msg('wrong_param')
        return JsonResponse(result)

    if otu.is_expired:
        result['message'] = get_error_msg('expired_token')
        return JsonResponse(result)

    f = otu.file
    otu.is_expired = True
    otu.save()

    if otu.type == "storage":
        f.storage = FileSystemStorage(location=settings.USER_STORAGE_ROOT)
    elif otu.type == "crash":
        f.storage = FileSystemStorage(location=settings.CRASH_STORAGE_ROOT)
    else:
        result['message'] = get_error_msg('unknown')
        return JsonResponse(result)

    response = FileResponse(f)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(f.name)

    return response


@require_POST
@apikey_required
def crash_upload(request):
    """
    Upload crash to server.

    :param request:
    :return:
    """
    result = {"result": False, "message": None}

    apikey = get_apikey(request)
    param_list = ["crashlog", "title"]
    if not check_param(request.POST, param_list):
        result['message'] = get_error_msg('wrong_param')
        return JsonResponse(result)

    param_list = ["file"]
    if not check_param(request.FILES, param_list):
        result['message'] = get_error_msg('wrong_param')
        return JsonResponse(result)

    # Get Parameters
    crash_log = request.POST['crashlog']
    title = request.POST['title']
    crash_file = request.FILES['file']
    crash_hash = hashlib.sha256(title.encode('utf-8')).hexdigest()
    is_duplicated_crash = False

    # Get fuzzer by API key
    try:
        fuzzer = Fuzzer.objects.get(api_key=apikey)
    except ObjectDoesNotExist:
        result['message'] = get_error_msg('wrong_apikey')
        return JsonResponse(result)

    # Get crash by crash_hash
    # If not exists, create new instance.
    try:
        crash = Crash.objects.get(crash_hash=crash_hash, parent_idx=0)
        is_duplicated_crash = True
    except ObjectDoesNotExist:
        crash = None

    # Create new crash
    new_crash = Crash(owner=fuzzer.owner, fuzzer=fuzzer)
    fuzzer.crash_cnt += 1

    # If duplicated crash
    if is_duplicated_crash:
        crash.dup_crash_cnt += 1
        new_crash.parent_idx = crash.id
        new_crash.is_dup_crash = True
        crash.save()
        fuzzer.save()

    # Common data
    new_crash.crash_hash = crash_hash
    new_crash.title = title
    new_crash.crash_log = crash_log
    new_crash.crash_file = crash_file
    new_crash.save()

    # Send alert message.
    # TODO : Send meesage via email or telegram

    result['result'] = True
    return JsonResponse(result)


@require_POST
@apikey_required
def fuzzer_update_info(request):
    """
    Update fuzzer's Public IP and Private IP.

    :param request:
    :return:
    """
    result = {"result": False, "message": None}

    apikey = get_apikey(request)
    param_list = ["public_ip", "private_ip"]
    if not check_param(request.POST, param_list):
        raise Http404

    public_ip = request.POST['public_ip']
    private_ip = request.POST['private_ip']

    try:
        validate_ipv4_address(public_ip)
        validate_ipv4_address(private_ip)
    except ValidationError:
        result["result"] = False
        result["message"] = "IP address is not valid."
        return JsonResponse(result)

    try:
        fuzzer = Fuzzer.objects.get(api_key=apikey)
    except ObjectDoesNotExist:
        result['message'] = get_error_msg('wrong_apikey')
        return JsonResponse(result)

    fuzzer.public_ip = public_ip
    fuzzer.private_ip = private_ip
    fuzzer.save()

    result['result'] = True
    return JsonResponse(result)


@require_GET
@apikey_required
def fuzzer_ping(request):
    """
    Send ping to server.

    :param request:
    :return:
    """
    result = {"result": False, "message": None}
    apikey = get_apikey(request)
    param_list = []
    if not check_param(request.POST, param_list):
        raise Http404

    try:
        fuzzer = Fuzzer.objects.get(api_key=apikey)
    except ObjectDoesNotExist:
        result['message'] = get_error_msg('wrong_apikey')
        return JsonResponse(result)

    fuzzer.ping_date = datetime.now()
    fuzzer.save()

    result['result'] = True
    return JsonResponse(result)


@require_GET
@apikey_required
def storage_list(request):
    """
    Get file list from storage

    :param request:
    :return:
    """
    result = {"result": False, "message": None}
    apikey = get_apikey(request)
    param_list = []
    if not check_param(request.POST, param_list):
        raise Http404

    try:
        fuzzer = Fuzzer.objects.get(api_key=apikey)
        storage = Storage.objects.filter(owner=fuzzer.owner)
    except ObjectDoesNotExist:
        result['message'] = get_error_msg('wrong_apikey')
        return JsonResponse(result)

    result['storage_list'] = []

    for f in storage:
        temp = {'idx': f.id, 'filename': f.original_name, 'size': f.file.size, 'reg_date': f.reg_date,
                'download_count': f.download_count, 'hash': f.hash, 'title': f.title}
        result['storage_list'].append(temp)
    return JsonResponse(result)


@require_POST
@apikey_required
def storage_download(request):
    result = {"result": False, "message": None}
    apikey = get_apikey(request)

    param_list = ['idx']
    if not check_param(request.POST, param_list):
        raise Http404

    idx = request.POST['idx']

    try:
        fuzzer = Fuzzer.objects.get(api_key=apikey)
        storage = Storage.objects.filter(owner=fuzzer.owner, id=idx)
    except ObjectDoesNotExist:
        result['message'] = get_error_msg('wrong_apikey')
        return JsonResponse(result)

    response = FileResponse(storage.file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(storage.name)

    return response


@require_GET
@login_required
def storage_download_web(request, idx):
    """
    Download file from storage server.

    :param request:
    :param idx:
    :return:
    """
    result = {"result": False, "message": None}

    try:
        storage = Storage.objects.get(owner=request.user, id=idx)
    except ObjectDoesNotExist:
        result['message'] = get_error_msg('wrong_param')
        return JsonResponse(result)

    response = FileResponse(storage.file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(storage.file.name)

    return response


@require_GET
@login_required
def storage_generate_url(request, idx):
    """
    Generate OTU for files in storage.

    :param request:
    :param idx:
    :return:
    """
    result = {"result": False, "message": None}

    try:
        storage = Storage.objects.get(owner=request.user, id=idx)
    except ObjectDoesNotExist:
        storage = None

    if not storage:
        result['message'] = get_error_msg('wrong_param')
        return JsonResponse(result)

    f = storage.file

    try:
        otu = OnetimeUrl.objects.get(owner=request.user, file=f, is_expired=False)
    except ObjectDoesNotExist:
        otu = None

    if not otu:
        otu = OnetimeUrl(owner=request.user, file=f, type="storage")
        otu.save()

    scheme = request.is_secure() and "https" or "http"
    result["result"] = True
    result["token"] = otu.token
    result["url"] = scheme + "://" + request.META['HTTP_HOST'] + "/api/v1/share/download?token=" + otu.token
    return JsonResponse(result)
