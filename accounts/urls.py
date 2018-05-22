from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.conf import settings

urlpatterns = [
    path('login', auth_views.login, name='accounts-login', kwargs={'template_name': 'accounts/login.html'}),
    path('logout', auth_views.logout, name='accounts-logout', kwargs={'next_page': settings.LOGIN_URL}),
]