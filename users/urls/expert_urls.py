from django.urls import path
from django.contrib.auth.views import LogoutView

from users.views import expert_views as views


urlpatterns = [
    path('list/', views.ExpertList.as_view(), name='expert_list'),
    path('add/', views.add, name='expert_add'),
    path('edit/<expert_id>/', views.edit, name='expert_edit')
]
