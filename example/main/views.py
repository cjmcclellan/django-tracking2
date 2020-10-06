from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView, FormView, View
from tracking.models import Visitor, Pageview
# from dash_cjm.plots.Plotting2DApp import StaticPlotting2DApp
# from django_plotly_dash import DjangoDash


# Create your views here.
class MainPage(TemplateView):

    # template_name = 'tracking/pageview.html'
    template_name = 'main/example.html'

    # def get(self, request, *args, **kwargs):
    #
    #     pageview_stats = Pageview.objects.stats()
    #     #
    #     context = {
    #         'pageview_stats': pageview_stats,
    #     }
    #
    #     # plot = StaticPlotting2DApp(name='tracking', y_variables=['number'], x_variables=['time'],
    #     #                            compute_function=lambda x: {'number': [0, 1], 'time': [7, 8], 'class': ['in']}, django=True, class_name='class')
    #
    #     # plot.build_app()
    #
    #     return render(request, self.template_name, context)
