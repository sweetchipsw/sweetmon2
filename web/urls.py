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

]