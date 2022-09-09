from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('display_results/<str:league>', views.display_results, name='display_results'),
    path('display_results/<str:league>/date', views.display_results, name='filter_results'),
]

