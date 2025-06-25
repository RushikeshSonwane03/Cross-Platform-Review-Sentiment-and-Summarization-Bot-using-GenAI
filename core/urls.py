from django.urls import path
from .import views

urlpatterns = [
    path('', views.home, name='home' ),
    path('load_csv/', views.load_csv, name='load_csv'),
    path('process/', views.process, name='process'),
    path('summerization/', views.summarize_reviews, name='summerization'),
    path('final_report/', views.final_report_view, name='final_report'),
]
