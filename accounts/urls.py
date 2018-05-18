from django.urls import include, path
from . import views

urlpatterns = [
    path('login', views.test, name='main-test'),
    path('logout', views.test1, name='main-test1'),
]