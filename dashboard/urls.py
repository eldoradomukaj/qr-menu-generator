from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('analyticsdata', views.analytics_data, name='analytics-data'),
    path('account/', views.account_view, name='account'),
    path('account/update/', views.account_update_view, name='update-account'),
    #path('manage/', views.create_menu, name='managemenu'),
    path('update/<str:pk>', views.menu_item_update_view, name='update-menu'),
    path('manage/', views.create_category, name='managemenu'),
    path('add/<slug:id>', views.add_by_category_view, name='category-add'),
    path('updatecategory/', views.category_update_view, name='update-category'),
    path('updatecategorysave/<int:pk>', views.save_category_update_view, name='save-category-update'),
    path('deleteitem/<str:pk>', views.menu_item_delete_view, name='delete-menu-item'),
    #path('qrcode/', views.qrcode_view, name='qrcode'),
    path('restaurant/', views.restaurant_info, name='restaurant'),
    path('restaurant/update/', views.restaurant_update_view, name='update-restaurant'),
    path('item/<pk>', views.item_detail, name='item-detail'),
    path('togglemenu/<int:pk>', views.set_menu_hidden_view, name='toggle-menu'),
    path('updateposition/<int:pk>', views.update_position_view, name='update-position'),
    path('deletemenuitem/<int:pk>', views.delete_menu_item, name='delete-menu-item'),
    path('deletecatitem/<int:pk>', views.delete_cat_item, name='delete-cat-item'),
    path('loadmenuitem/', views.load_menu_item, name='load-menu-item'),
    path('updatemenuitem/<int:pk>', views.update_menu_item, name='update-menu-item'),
    path('hidecategory/', views.hide_category_view, name='hide-category'),
    path('fetchorders/', views.fetch_orders_view, name='fetch-orders'),
    path('publishmenu/', views.publish_menu_view, name='publish-menu'),
    path('removeimage/', views.remove_image_view, name='remove-image'),
    path('removemenuimage/', views.remove_menu_item_image, name='remove-menu-image')
]