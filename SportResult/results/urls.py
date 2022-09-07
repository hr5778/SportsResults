from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('nba_results/', views.nba_results, name='nba_results'),
]

