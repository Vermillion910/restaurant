from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('menu/', views.menu, name='menu'),
    path('reserve/', views.make_reservation, name='make_reservation'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    path('cancel/<int:pk>/', views.cancel_reservation, name='cancel_reservation'),
    path('order-food/<int:reservation_id>/', views.order_food, name='order_food'),
    path('add-to-order/<int:reservation_id>/<int:item_id>/', views.add_to_order, name='add_to_order'),
    path('remove-from-order/<int:item_id>/', views.remove_from_order, name='remove_from_order'),
    path('update-order-item/<int:item_id>/<str:action>/', views.update_order_item, name='update_order_item'),
    path('profile/', views.profile, name='profile'),
    path('add-favorite/<int:item_id>/', views.add_favorite, name='add_favorite'),
    path('remove-favorite/<int:item_id>/', views.remove_favorite, name='remove_favorite'),
    path('repeat-order/<int:reservation_id>/', views.repeat_order, name='repeat_order'),
    path('events/', views.events, name='events'),
    path('events/', views.events, name='events'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
]