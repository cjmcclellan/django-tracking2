from django.conf.urls import url
from django.urls import path

from tracking.views import dashboard, ConDashboard

urlpatterns = [
    # url(r'^$', dashboard, name='tracking-dashboard'),
    path('', ConDashboard.as_view())
]
