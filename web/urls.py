from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.index, name='main-statistics'),

    path('crash/', views.crash, name='crash-list'),
    path('crash/<int:idx>', views.crash_detail, name='crash-info'),

    path('fuzzer/', views.fuzzer, name='fuzzer-list'),
    path('fuzzer/<int:idx>', views.fuzzer_detail, name='fuzzer-info'),

    path('docs/api', views.api_docs, name='api-docs'),

    path('client/', views.sweetmon_client, name='sweetmon-client-docs'),

    path('storage/', views.storage, name='storage'),
    path('storage/<int:idx>', views.storage_detail, name='storage-detail'),

    # Web API
    path('crash/generate_url', views.crash_generate_url, name='crash-generate-OTU'),
    path('storage/generate_url', views.storage_generate_url, name='storage-generate-OTU'),  # Web API
    path('storage/<int:idx>/download', views.storage_download_web, name='storage-download-on-web'),  # Web API
    path('crash/<int:idx>/download', views.crash_download, name='crash-download-directly'),
    path('crash/<int:idx>/duplicated_list', views.crash_dup_crash_list, name='crash-duplicated-crash'),
    path('crash/favorite', views.crash_favorite, name='crash-favorite-crash'),


]