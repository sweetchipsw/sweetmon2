from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.http import Http404
import hashlib
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
from django.utils.crypto import get_random_string
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from api.models import Fuzzer, Crash, Storage
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from pprint import pprint
from itertools import groupby
from django.db.models.functions import TruncMonth, TruncDay
import time
import json


@login_required
def index(request):
    startdate = datetime.today() - timedelta(days=6)
    enddate = datetime.today()


    try:
        fuzzer = Fuzzer.objects.filter(owner=request.user)
        crash = Crash.objects.filter(owner=request.user)
        unique_crash = Crash.objects.filter(owner=request.user, parent_idx=0)
        total_crash = Crash.objects.all()
        storage = Storage.objects.filter(owner=request.user)
        user = User.objects.all()
        last_7day_crashes = Crash.objects.filter(reg_date__range=[startdate, enddate]).annotate(month=TruncDay('reg_date')).values('month').annotate(c=Count('id')).order_by()
    except ObjectDoesNotExist:
        raise Http404

    last_7day_crashes_dict = dict()
    last_7day_crashes_list = list()

    for day in range(5, -2, -1):
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

    context = {'crash': crash, 'fuzzer': fuzzer, 'storage':storage, 'crash_list': unique_crash[:5], 'fuzzer_list': fuzzer[:5],
               'storage_list': storage, 'user': user, "unique_crash": unique_crash, "total_crash": total_crash,
               "last_7day_crashes_dict": json.dumps(last_7day_crashes_list), 'active_time': active_time}
    return render(request, 'web/index.html', context)


@login_required
def fuzzer(request):
    try:
        fuzzer = Fuzzer.objects.filter(owner=request.user)
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
    context = {'fuzzer': fuzzer}
    return render(request, 'web/fuzzer_detail.html', context)


@login_required
def crash(request):
    try:
        crash = Crash.objects.filter(owner=request.user, is_dup_crash=False, parent_idx=0)
    except ObjectDoesNotExist:
        raise Http404

    paginator = Paginator(crash, 100)
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

    context = {'crash_list': crash, 'paginator': paginator, 'page_range': page_range}
    return render(request, 'web/crash.html', context)


@login_required
def crash_detail(request, idx):
    # Get crash by idx
    try:
        crash = Crash.objects.get(owner=request.user, id=idx)
    except ObjectDoesNotExist:
        raise Http404

    # Get duplicated crash
    try:
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
