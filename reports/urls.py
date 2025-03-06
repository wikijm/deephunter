from django.urls import path
from . import views

urlpatterns = [
    path('campaigns_stats', views.campaigns_stats, name='campaigns_stats'),
    path('analytics_perfs', views.analytics_perfs, name='analytics_perfs'),
    path('mitre', views.mitre, name='mitre'),
    path('endpoints', views.endpoints, name='endpoints'),
    path('missing_mitre', views.missing_mitre, name='missing_mitre'),
]
