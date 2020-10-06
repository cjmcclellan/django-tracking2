from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
from . import views
# from django_plotly_dash.views import add_to_session


urlpatterns = [
    path('', views.MainPage.as_view()),
    url(r'^tracking/', include('tracking.urls')),
]
