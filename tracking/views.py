import logging

from datetime import timedelta
from django.views.generic import TemplateView

from django import forms
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.timezone import now
from django.http import HttpResponse

from tracking.models import Visitor, Pageview
from tracking.settings import TRACK_PAGEVIEWS
# from dash_cjm.plots.Plotting2DApp import StaticPlotting2DApp
from tracking.dashboard import TrackingDashboard


log = logging.getLogger(__file__)

# tracking wants to accept more formats than default, here they are
input_formats = [
    '%Y-%m-%d %H:%M:%S',    # '2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M',       # '2006-10-25 14:30'
    '%Y-%m-%d',             # '2006-10-25'
    '%Y-%m',                # '2006-10'
    '%Y',                   # '2006'
]


class DashboardForm(forms.Form):
    start = forms.DateTimeField(required=False, input_formats=input_formats)
    end = forms.DateTimeField(required=False, input_formats=input_formats)


def record_mouse_click(request):
    visitor = Visitor.objects.get(session_key__exact=request.session.session_key)
    visitor.mouse_click = True
    visitor.save()
    return HttpResponse('')


def record_mouse_movement(request):
    visitor = Visitor.objects.get(session_key__exact=request.session.session_key)
    visitor.mouse_movement = True
    visitor.save()
    return HttpResponse('')


@permission_required('tracking.visitor_log')
def dashboard(request):
    "Counts, aggregations and more!"
    end_time = now()
    start_time = end_time - timedelta(days=7)
    defaults = {'start': start_time, 'end': end_time}

    form = DashboardForm(data=request.GET or defaults)
    if form.is_valid():
        start_time = form.cleaned_data['start']
        end_time = form.cleaned_data['end']

    # determine when tracking began
    try:
        obj = Visitor.objects.order_by('start_time')[0]
        track_start_time = obj.start_time
    except (IndexError, Visitor.DoesNotExist):
        track_start_time = now()

    # If the start_date is before tracking began, warn about incomplete data
    warn_incomplete = (start_time < track_start_time)

    # queries take `date` objects (for now)
    user_stats = Visitor.objects.user_stats(start_time, end_time)
    visitor_stats = Visitor.objects.stats(start_time, end_time)
    if TRACK_PAGEVIEWS:
        pageview_stats = Pageview.objects.stats(start_time, end_time)
    else:
        pageview_stats = None

    context = {
        'form': form,
        'track_start_time': track_start_time,
        'warn_incomplete': warn_incomplete,
        'user_stats': user_stats,
        'visitor_stats': visitor_stats,
        'pageview_stats': pageview_stats,
    }
    return render(request, 'tracking/dashboard.html', context)


# Create your views here.
# @permission_required('tracking.visitor_log')
class ConDashboard(LoginRequiredMixin, TemplateView):

    template_name = 'tracking/pageview.html'

    def get(self, request, *args, **kwargs):

        # pageview_stats = Pageview.objects.stats()
        #
        # context = {
        #     'pageview_stats': pageview_stats,
        # }

        dash = TrackingDashboard(name='test', django=True)

        # plot = StaticPlotting2DApp(name='tracking_time', y_variables=['number'], x_variables=['time'],
        #                            compute_function=lambda x: {'number': [0, 1], 'time': [7, 8]}, django=False, class_name='class')

        # plot.build_app()
        # plot.app.run_server(debug=True)
        return render(request, self.template_name)
        # return render(request, self.template_name, context)
