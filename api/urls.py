from django.urls import include, path
from . import views

urlpatterns = [
    # One time url 랙 ㅉ뜌 몌ㅑ
    path('share/download', views.file_download_by_otu, name='Download-file-by-OTU'),

    # Internal API
    path('crash/<int:idx>/download', views.crash_download, name='crash-download-directly'),
    path('crash/<int:idx>/generate_url', views.crash_generate_url, name='crash-generate-OTU'),
    path('crash/<int:idx>/duplicated_list', views.crash_dup_crash_list, name='crash-duplicated-crash'),

    # APIs for interacting with clients.
    path('crash/upload', views.crash_upload, name='crash-upload-crash'),

    path('fuzzer/update_info', views.fuzzer_update_info, name='fuzzer-update-client'),
    path('fuzzer/ping', views.fuzzer_ping, name='fuzzer-ping'),


    path('storage/list', views.storage_list, name='storage-list'),  # API
    path('storage/download', views.storage_download, name='storage-download'),  # API

    # APIs for web
    path('storage/<int:idx>/download', views.storage_download_web, name='storage-download-on-web'),  # Web API
    path('storage/<int:idx>/generate_url', views.storage_generate_url, name='storage-generate-OTU'),  # Web API

]
