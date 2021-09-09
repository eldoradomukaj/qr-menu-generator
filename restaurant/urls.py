from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('getorder/', views.get_order_items, name='getorder'),
    path('<str:pk>/favorites/', views.get_favorites_view, name='favorites'),
    path('<str:pk>/addfavorite/', views.add_favorites_view, name='add-favorites'),
    path('<str:pk>/order/', views.order_view, name='order'),
    #path('<str:pk>/checkout/order', views.inrestaurant_checkout_view, name='restaurant-checkout'),
    #path('<str:pk>/order/removeitem', views.remove_order_item, name='remove-order-item'),
    #path('<str:pk>/checkout/carryout', views.carryout_checkout_view, name='carryout'),
    path('<str:pk>/', views.restaurant_view, name='menu'),
    path('<str:pk>/order/changequantity', views.modify_item_quantity, name='modify-item-quantity'),
    path('<str:pk>/<slug:id>/', views.category_view, name='category'),
    path('<str:pk>/<slug:cat_id>/<int:item_id>', views.item_view, name='item')
]
