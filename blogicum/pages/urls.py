from django.urls import path
# from django.views.generic import TemplateView

from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.AbutView.as_view(), name='about'),
    path('rules/', views.RulesView.as_view(), name='rules'),
]
