from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
from django_plotly_dash.views import add_to_session


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    # url(r'^tracking/', include('tracking.urls')),
    path('', include(('main.urls', 'main'))),
]
