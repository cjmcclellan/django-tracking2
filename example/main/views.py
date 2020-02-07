from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView, FormView, View
from tracking.models import Visitor, Pageview


# Create your views here.
class MainPage(TemplateView):

    template_name = 'tracking/pageview.html'

    def get(self, request, *args, **kwargs):

        pageview_stats = Pageview.objects.stats()

        context = {
            'pageview_stats': pageview_stats,
        }
        return render(request, self.template_name, context)
