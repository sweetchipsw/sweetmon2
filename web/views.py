from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.shortcuts import render,get_object_or_404
from django.http import Http404, FileResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from api.models import Fuzzer, Crash, Storage, OnetimeUrl
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.functions import TruncMonth, TruncDay
from django.utils.crypto import get_random_string
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.conf import settings
from pprint import pprint
from itertools import groupby
import time
import hashlib
import json


def get_error_msg(key):
    error_list = {"wrong_apikey": "Invalid API Key.",
                  "wrong_param": "Invalid parameter.",
                  "unknown": "Unknown error",
                  "expired_token": "Token expired."}
    return error_list[key]


def check_param(request_method, parameter):
    for param in parameter:
        if param not in request_method:
            return False
    return True


@login_required
def index(request):
    startdate = datetime.today() - timedelta(days=6)
    enddate = datetime.today()

    try:
        fuzzer = Fuzzer.objects.order_by('report_date').filter(owner=request.user)
    except ObjectDoesNotExist:
        fuzzer = []

    try:
        crash = Crash.objects.filter(owner=request.user)[::-1]
    except ObjectDoesNotExist:
        crash = []

    try:
        unique_crash = Crash.objects.filter(owner=request.user, parent_idx=0)
    except ObjectDoesNotExist:
        unique_crash = []

    try:
        total_crash = Crash.objects.filter(owner=request.user)
    except ObjectDoesNotExist:
        total_crash = []

    try:
        storage = Storage.objects.filter(owner=request.user)
    except ObjectDoesNotExist:
        storage = []

    try:
        last_7day_crashes = Crash.objects.filter(owner=request.user, reg_date__range=[startdate, enddate]).annotate(
            month=TruncDay('reg_date')).values('month').annotate(c=Count('id')).order_by()
    except ObjectDoesNotExist:
        last_7day_crashes = []

    try:
        user = User.objects.all()
    except ObjectDoesNotExist:
        context = {}
        return render(request, 'web/index.html', context)

    last_7day_crashes_dict = dict()
    last_7day_crashes_list = list()

    for day in range(6, -2, -2):
        date = datetime.today() - timedelta(days=day)
        date = date.strftime('%Y-%m-%d')
        last_7day_crashes_dict[date] = 0

    for day_crash in last_7day_crashes:
        date = day_crash['month'].strftime('%Y-%m-%d')
        last_7day_crashes_dict[date] = day_crash['c']

    for last_7day_crash in last_7day_crashes_dict:
        temp_dict = dict()
        temp_dict['x'] = last_7day_crash
        temp_dict['y'] = last_7day_crashes_dict[last_7day_crash]
        last_7day_crashes_list.append(temp_dict)

    active_time = datetime.now() - timedelta(minutes=5)

    last_crash = []

    if len(crash) > 0:
        last_crash = crash[0]

    context = {'crash': crash, 'fuzzer': fuzzer, 'storage':storage, 'crash_list': unique_crash[::-1][:5], 'fuzzer_list': fuzzer[:5],
               'storage_list': storage, 'user': user, "unique_crash": unique_crash, "total_crash": total_crash,
               "last_7day_crashes_dict": json.dumps(last_7day_crashes_list), 'active_time': active_time, 'last_crash': last_crash}
    return render(request, 'web/index.html', context)


@login_required
def fuzzer(request):
    try:
        fuzzer = Fuzzer.objects.filter(owner=request.user)[::-1]
    except ObjectDoesNotExist:
        raise Http404

    paginator = Paginator(fuzzer, 50)
    page = request.GET.get('p', 1)
    try:
        fuzzer = paginator.page(page)
    except PageNotAnInteger:
        fuzzer = paginator.page(1)
    except EmptyPage:
        fuzzer = paginator.page(paginator.num_pages)

    if page not in paginator.page_range:
        paginator.page(1)

    index = paginator.page_range.index(fuzzer.number)
    max_index = len(paginator.page_range)
    start_index = index - 5 if index >= 5 else 0
    end_index = index + 5 if index <= max_index - 5 else max_index
    page_range = paginator.page_range[start_index:end_index]

    active_time = datetime.now() - timedelta(minutes=5)
    context = {'fuzzer_list': fuzzer, 'active_time': active_time, 'paginator': paginator, 'page_range': page_range}
    return render(request, 'web/fuzzer.html', context)


@login_required
def fuzzer_detail(request, idx):
    try:
        fuzzer = Fuzzer.objects.get(owner=request.user, id=idx)
    except ObjectDoesNotExist:
        raise Http404
    active_time = datetime.now() - timedelta(minutes=5)

    context = {'fuzzer': fuzzer, 'active_time': active_time}
    return render(request, 'web/fuzzer_detail.html', context)


@login_required
def crash(request):
    mode = request.GET.get('m', 0)
    try:
        # Mode 1 : Show all of new crashes.
        if mode == "1":
            crash_items = Crash.objects.filter(owner=request.user)[::-1]
        else:
            # Mode 0 : Default, Show crashes without duplicated one.
            crash_items = Crash.objects.filter(owner=request.user, is_dup_crash=False, parent_idx=0)[::-1]

    except ObjectDoesNotExist:
        raise Http404

    paginator = Paginator(crash_items, 50)
    page = request.GET.get('p', 1)
    try:
        crash_items = paginator.page(page)
    except PageNotAnInteger:
        crash_items = paginator.page(1)
    except EmptyPage:
        crash_items = paginator.page(paginator.num_pages)

    if page not in paginator.page_range:
        paginator.page(1)

    idx = paginator.page_range.index(crash_items.number)
    max_index = len(paginator.page_range)
    start_index = idx - 5 if idx >= 5 else 0
    end_index = idx + 5 if idx <= max_index - 5 else max_index
    page_range = paginator.page_range[start_index:end_index]

    context = {'crash_list': crash_items, 'paginator': paginator, 'page_range': page_range, 'mode': mode}
    return render(request, 'web/crash.html', context)


@login_required
def crash_detail(request, idx):
    # Get crash by idx
    try:
        crash = Crash.objects.get(owner=request.user, id=idx)
    except ObjectDoesNotExist:
        raise Http404

    # If post (save comment)

    if request.method == "POST":
        param_list = ['comment']
        if check_param(request.POST, param_list):
            comment = request.POST['comment']
            crash.comment = comment
            crash.save()

    # Get duplicated crash
    try:
        if crash.is_dup_crash:
            dup_crash = Crash.objects.filter(owner=request.user, parent_idx=crash.parent_idx)[::-1]
        else:
            dup_crash = Crash.objects.filter(owner=request.user, is_dup_crash=True, parent_idx=idx)[::-1]
    except ObjectDoesNotExist:
        raise Http404

    paginator = Paginator(dup_crash, 30)
    page = request.GET.get('p', 1)
    try:
        dup_crash = paginator.page(page)
    except PageNotAnInteger:
        dup_crash = paginator.page(1)
    except EmptyPage:
        dup_crash = paginator.page(paginator.num_pages)

    if page not in paginator.page_range:
        paginator.page(1)

    index = paginator.page_range.index(dup_crash.number)
    max_index = len(paginator.page_range)
    start_index = index - 5 if index >= 5 else 0
    end_index = index + 5 if index <= max_index - 5 else max_index
    page_range = paginator.page_range[start_index:end_index]

    context = {'crash': crash, 'dup_crash_list': dup_crash, 'paginator': paginator, 'page_range': page_range}
    return render(request, 'web/crash_detail.html', context)


@login_required
def storage(request):
    try:
        storage = Storage.objects.filter(owner=request.user)
    except ObjectDoesNotExist:
        raise Http404

    paginator = Paginator(storage, 30)
    page = request.GET.get('p', 1)
    try:
        storage = paginator.page(page)
    except PageNotAnInteger:
        storage = paginator.page(1)
    except EmptyPage:
        storage = paginator.page(paginator.num_pages)

    if page not in paginator.page_range:
        paginator.page(1)

    index = paginator.page_range.index(storage.number)
    max_index = len(paginator.page_range)
    start_index = index - 5 if index >= 5 else 0
    end_index = index + 5 if index <= max_index - 5 else max_index
    page_range = paginator.page_range[start_index:end_index]

    context = {'storage_list': storage, 'paginator': paginator, 'page_range': page_range}
    return render(request, 'web/storage.html', context)


@login_required
def storage_detail(request, idx):
    try:
        storage = Storage.objects.get(owner=request.user, id=idx)
    except ObjectDoesNotExist:
        raise Http404
    context = {'storage': storage}
    return render(request, 'web/storage_detail.html', context)


@login_required
def api_docs(request):
    context = {}
    return render(request, 'web/api_docs.html', context)


@login_required
def sweetmon_client(request):
    context = {}
    return render(request, 'web/sweetmon_client.html', context)


def error_not_found(request):
    return render(request, 'web/common/404.html')


def error_internal_error(request):
    return render(request, 'web/common/500.html')

@require_POST
@login_required
def storage_generate_url(request):
    """
    Generate OTU for files in storage.

    :param request:
    :param idx:
    :return:
    """
    result = {"result": False, "message": None}

    param_list = ["idx"]
    if not check_param(request.POST, param_list):
        result['message'] = get_error_msg('wrong_param')
        return JsonResponse(result)

    idx = request.POST['idx']

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
        otu = OnetimeUrl(owner=request.user, file=f, type="storage", content_object=storage)
        otu.save()

    scheme = request.is_secure() and "https" or "http"
    result["result"] = True
    result["token"] = otu.token
    result["url"] = scheme + "://" + request.META['HTTP_HOST'] + "/api/v1/share/download?token=" + otu.token
    return JsonResponse(result)


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

    storage.download_count += 1
    storage.save()

    fname = storage.file.name
    if "/" in fname:
        fname = fname.split("/")[-1]

    response = FileResponse(storage.file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(fname)

    return response


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
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(crash.file_hash)

    return response


@require_POST
@login_required
def crash_generate_url(request):
    result = {"result": False, "message": None}

    param_list = ["idx"]
    if not check_param(request.POST, param_list):
        result['message'] = get_error_msg('wrong_param')
        return JsonResponse(result)

    idx = request.POST['idx']

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
        otu = OnetimeUrl(owner=request.user, file=f, type="crash", content_object=crash)
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

