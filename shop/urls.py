from django.urls import path
from . import views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list_view, name='product_list'),
    path('ajax-product-list/', views.ajax_product_list_view, name='ajax_product_list'),
    path('recent-orders/', views.recent_orders_view, name='recent_orders'),
]