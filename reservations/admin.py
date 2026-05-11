from django.contrib import admin
from .models import Reservation, MenuCategory, MenuItem, Order, OrderItem
from .models import Event



@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['user_number', 'user', 'first_name', 'last_name', 'date', 'time', 'guests_count', 'status']
    list_filter = ['status', 'date']

@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available']
    list_filter = ['category', 'is_available']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'reservation', 'status', 'total_price', 'created_at']
    list_filter = ['status']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'menu_item', 'quantity', 'price']



@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'is_active']
