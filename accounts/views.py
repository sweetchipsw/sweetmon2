from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse


def login(request):
    return render(request, 'accounts/login.html')


def logout(request):
    return HttpResponseRedirect("/accounts/login")
