from django.conf.urls import url
from django.urls import path
from tracking.views import dashboard, ConDashboard, record_mouse_click

urlpatterns = [
    # url(r'^$', dashboard, name='tracking-dashboard'),
    path('', ConDashboard.as_view()),
    path('ajax/mouse_click', record_mouse_click, name='mouse_click'),
    # path('ajax/mouse_movement', record_mouse_click, name='mouse_click')
]
