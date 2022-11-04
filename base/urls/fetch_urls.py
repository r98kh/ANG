from django.urls import path

from base.views import fetch_views as views

urlpatterns = [
    path('get-city/', views.get_city),

    path('get-features/', views.get_features),
    path('get-feature-details/', views.get_feature_details),

    path('filter-color/', views.filter_color),

    path('get-product-features/', views.get_product_features),

    path('pre-order-edit/', views.pre_order_edit),
    path('pre-order-delete/', views.pre_order_delete),
    path('order-complete/', views.order_complete),
    path('admin/order-complete/', views.admin_order_complete),
    path('order-change-status/', views.order_change_status),

    path('update-status/', views.update_status),

    path('featurevalue-edit/', views.featurevalue_edit),
]
