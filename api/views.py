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
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import decorator_from_middleware
from django.middleware.http import ConditionalGetMiddleware
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import *
from django.db.models.functions import TruncMonth, TruncDay
from api.models import Crash, Storage, Fuzzer, OnetimeUrl
from accounts.models import Profile
from django.db.models import Count
from datetime import datetime, timedelta
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
    fname = ""
    if otu.type == "storage":
        f.storage = FileSystemStorage(location=settings.USER_STORAGE_ROOT)
        fname = otu.content_object.file.name
        otu.content_object.download_count += 1
        otu.content_object.save()
        if "/" in fname:
            fname = fname.split("/")[-1]
    elif otu.type == "crash":
        f.storage = FileSystemStorage(location=settings.CRASH_STORAGE_ROOT)
        fname = otu.content_object.file_hash
    else:
        result['message'] = get_error_msg('unknown')
        return JsonResponse(result)

    response = FileResponse(f)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename={0};filename*=UTF-8\'\'"{1}"'.format(fname, fname)

    return response


@csrf_exempt
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
        crash = Crash.objects.get(title_hash=crash_hash, parent_idx=0)
        is_duplicated_crash = True
    except ObjectDoesNotExist:
        crash = None

    # Create new crash
    new_crash = Crash(owner=fuzzer.owner, fuzzer=fuzzer)
    fuzzer.crash_cnt += 1
    fuzzer.save()

    # If duplicated crash
    if is_duplicated_crash:
        crash.dup_crash_cnt += 1
        new_crash.parent_idx = crash.id
        new_crash.is_dup_crash = True
        crash.save()

    # Common data
    new_crash.title_hash = crash_hash
    new_crash.title = title
    new_crash.crash_log = crash_log
    new_crash.crash_file = crash_file
    new_crash.save()

    # Save again.
    file_hash = hashlib.sha256(new_crash.crash_file.read()).hexdigest()
    new_crash.file_hash = file_hash
    new_crash.save()

    # Send alert message.
    # TODO : Send meesage via email or telegram

    result['result'] = True
    return JsonResponse(result)


@csrf_exempt
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
    result['result'] = True
    return JsonResponse(result)


@csrf_exempt
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

    storage.download_count += 1
    storage.save()

    response = FileResponse(storage.file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(storage.name)

    return response


@require_GET
@apikey_required
def get_fuzzer_list(request):
    """
    Get all of fuzzers.

    :param request:
    :return:
    """
    result = {"result": False, "message": None}
    #apikey = get_apikey(request)

    apikey = "817033960af85e4f9ac18cc1be4e88aeb399d23b27a852d321692e127c142425"

    try:
        profile = Profile.objects.get(api_key=apikey)
        user = profile.owner
    except ObjectDoesNotExist:
        result['message'] = get_error_msg("wrong_apikey")
        return JsonResponse(result)

    if not profile.use_user_api:
        result['message'] = "You do not have permission to use 'user api'." \
                            "Please turn on your user api setting on admin page."
        return JsonResponse(result)
    try:
        fuzzers = Fuzzer.objects.filter(owner=profile.owner)
    except:
        fuzzers = []
        result['data'] = []
        return JsonResponse(result)

    result_fuzzers = []
    for fuzzer in fuzzers:
        tmp_fuzzer = dict()
        tmp_fuzzer['id'] = fuzzer.id
        tmp_fuzzer['name'] = fuzzer.name
        tmp_fuzzer['description'] = fuzzer.description
        tmp_fuzzer['crash_count'] = fuzzer.crash_cnt
        tmp_fuzzer['public_ip'] = fuzzer.public_ip
        tmp_fuzzer['private_ip'] = fuzzer.private_ip
        tmp_fuzzer['reg_date'] = fuzzer.reg_date
        tmp_fuzzer['last_ping_date'] = fuzzer.ping_date
        tmp_fuzzer['last_report_date'] = fuzzer.report_date
        tmp_fuzzer['api_key'] = fuzzer.api_key
        result_fuzzers.append(tmp_fuzzer)

    result['result'] = True
    result['data'] = result_fuzzers
    return JsonResponse(result)


@require_GET
#@apikey_required
def get_status_all(request):
    """
    Get statistics of sweetmon2.

    :param request:
    :return:
    """
    result = {"result": False, "message": None}
    #apikey = get_apikey(request)
    apikey = "817033960af85e4f9ac18cc1be4e88aeb399d23b27a852d321692e127c142425"

    try:
        profile = Profile.objects.get(api_key=apikey)
        user = profile.owner
    except ObjectDoesNotExist:
        result['message'] = get_error_msg("wrong_apikey")
        return JsonResponse(result)

    if not profile.use_user_api:
        result['message'] = "You do not have permission to use 'user api'." \
                            "Please turn on your user api setting on admin page."
        return JsonResponse(result)

    try:
        fuzzer = Fuzzer.objects.filter(owner=user)
    except ObjectDoesNotExist:
        fuzzer = []

    try:
        crash = Crash.objects.filter(owner=user)[::-1]
    except ObjectDoesNotExist:
        crash = []

    try:
        unique_crash = Crash.objects.filter(owner=user, parent_idx=0)
    except ObjectDoesNotExist:
        unique_crash = []

    try:
        storage = Storage.objects.filter(owner=user)
    except ObjectDoesNotExist:
        storage = []

    # for dbg
    apikey = "817033960af85e4f9ac18cc1be4e88aeb399d23b27a852d321692e127c142425"

    info = dict()
    info['username'] = user.username
    info['fuzzer_count'] = len(fuzzer)
    info['crash_count'] = len(crash)
    info['unique_crash_count'] = len(unique_crash)
    info['storage_files_count'] = len(storage)

    result['data'] = info
    result['result'] = True
    return JsonResponse(result)


@csrf_exempt
@require_POST
@apikey_required
def create_fuzzer(request):
    """
    Create new fuzzer on sweetmon2.

    :param request:
    :return:
    """
    result = {"result": False, "message": None}
    apikey = get_apikey(request)

    try:
        profile = Profile.objects.get(api_key=apikey)
        user = profile.owner
    except ObjectDoesNotExist:
        result['message'] = get_error_msg("wrong_apikey")
        return JsonResponse(result)

    if not profile.use_user_api:
        result['message'] = "You do not have permission to use 'user api'." \
                            "Please turn on your user api setting on admin page."
        return JsonResponse(result)

    param_list = ["name", "target", "description"]
    if not check_param(request.POST, param_list):
        raise Http404

    name = request.POST['name']
    target = request.POST['target']
    description = request.POST['description']

    fuzzer = Fuzzer(owner=user, name=name, target=target, description=description)
    fuzzer.save()

    tmp_fuzzer = dict()
    tmp_fuzzer['id'] = fuzzer.id
    tmp_fuzzer['name'] = fuzzer.name
    tmp_fuzzer['description'] = fuzzer.description
    tmp_fuzzer['crash_count'] = fuzzer.crash_cnt
    tmp_fuzzer['public_ip'] = fuzzer.public_ip
    tmp_fuzzer['private_ip'] = fuzzer.private_ip
    tmp_fuzzer['reg_date'] = fuzzer.reg_date
    tmp_fuzzer['last_ping_date'] = fuzzer.ping_date
    tmp_fuzzer['last_report_date'] = fuzzer.report_date
    tmp_fuzzer['api_key'] = fuzzer.api_key

    result['data'] = tmp_fuzzer
    result['result'] = True
    return JsonResponse(result)












