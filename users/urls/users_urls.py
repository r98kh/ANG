from django.urls import path
from django.contrib.auth.views import LogoutView

from users.views import user_views as views


urlpatterns = [
    path('profile/', views.profile, name="profile"),
    path('register/', views.register, name="register"),
    path('login/', views.user_login, name="login"),
    path('confirm/', views.confirm, name='confirm'),
    path('logout/', LogoutView.as_view(template_name="auth/login.html"), name='logout'),

    path('list/', views.UserList.as_view(), name='users_list'),
    path('add/', views.add, name='user_add'),
    path('edit/<user_id>/', views.edit, name='user_edit'),
    # path('delete/<p_id>/', views.delete, name='user_delete'),
]
