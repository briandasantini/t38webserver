from django.urls import path
from public import views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("tutorial/", views.TutorialPageView.as_view(), name="tutorial"),
    path("results/", views.ResultPageView.as_view(), name="result_page"),
    path('download/', views.download_file, name="download"),
]