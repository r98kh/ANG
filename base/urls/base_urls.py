from django.urls import path

from base.views import base_views as views


urlpatterns = [
    path('', views.dashboard_user, name="dashboard_user"),
    path('admin/', views.dashboard_admin, name='dashboard_admin'),
]
