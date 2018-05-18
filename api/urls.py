from django.urls import include, path
from . import views

urlpatterns = [
    # Internal API
    path('crash/download', views.test1, name='crash-generate-download'),
    path('crash/generate_url', views.test1, name='crash-generate-OTU'),

    # API for interacting with clients.
    path('crash/upload', views.test1, name='crash-upload-crash'),
    path('fuzzer/update_info', views.test1, name='fuzzer-update-client'),
    path('fuzzer/ping', views.test1, name='fuzzer-ping'),

    # ETC
    path('health', views.test1, name='health-checker'),
]