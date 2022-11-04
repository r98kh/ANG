from django.urls import path

from base.views import order_views as views

urlpatterns = [
    path('list/', views.OrderList.as_view(), name='order_list'),
    path('admin/list/', views.AdminOrderList.as_view(), name='admin_order_list'),
    path('add/', views.add, name="order_add"),
    path('admin/add/', views.admin_add, name="admin_order_add"),
    path('detail/<order_id>/', views.detail, name='order_detail'),
    path('invoice/<order_id>/', views.invoice, name='order_invoice'),

]
