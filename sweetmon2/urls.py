from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('web.urls')),
]


# handler404 = 'web.views.error_page_notfound'
# handler500 = 'web.views.error_internal_error'
#