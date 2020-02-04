from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^tracking/', include('tracking.urls')),
    path('', include(('main.urls', 'main'))),
]
