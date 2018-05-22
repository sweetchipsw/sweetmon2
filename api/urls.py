from django.urls import include, path
from . import views

urlpatterns = [
    # Internal API
    path('crash/download', views.crash_download, name='crash-generate-download'),
    path('crash/generate_url', views.crash_generate_url, name='crash-generate-OTU'),

    # API for interacting with clients.
    path('crash/upload', views.crash_upload, name='crash-upload-crash'),

    path('fuzzer/update_info', views.fuzzer_update_info, name='fuzzer-update-client'),
    path('fuzzer/ping', views.fuzzer_ping, name='fuzzer-ping'),

    path('storage/list', views.storage_list, name='storage-list'),
    path('storage/download', views.storage_download, name='storage-download'),

    # ETC
    path('health', views.health, name='health-checker'),
]