from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from .models import Reservation, MenuCategory, Order, OrderItem, MenuItem, Event
from .forms import ReservationForm, RegistrationForm
from .forms import ProfileForm
from .models import Favorite


def home(request):
    """Главная страница"""
    return render(request, 'reservations/home.html')


def register(request):
    """Регистрация пользователя"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать!')
            return redirect('home')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = RegistrationForm()
    return render(request, 'reservations/register.html', {'form': form})


@login_required
def make_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.save()
            messages.success(request, f'Бронирование №{reservation.user_number} создано! Теперь вы можете заказать блюда.')
            return redirect('order_food', reservation_id=reservation.id)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = ReservationForm()
    return render(request, 'reservations/make_reservation.html', {'form': form})

@login_required
def my_reservations(request):
    """Мои бронирования и избранное"""
    reservations = Reservation.objects.filter(user=request.user).order_by('-created_at')
    favorites = Favorite.objects.filter(user=request.user).select_related('menu_item')
    return render(request, 'reservations/my_reservations.html', {
        'reservations': reservations,
        'favorites': [f.menu_item for f in favorites]
    })

def menu(request):
    """Страница с меню"""
    categories = MenuCategory.objects.prefetch_related('menuitem_set').all()
    if request.user.is_authenticated:
        user_favorites = Favorite.objects.filter(user=request.user).values_list('menu_item_id', flat=True)
    else:
        user_favorites = []
    return render(request, 'reservations/menu.html', {
        'categories': categories,
        'user_favorites': user_favorites,
    })

@login_required
def order_food(request, reservation_id):
    """Страница заказа еды после бронирования"""
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    categories = MenuCategory.objects.prefetch_related('menuitem_set').all()
    order, created = Order.objects.get_or_create(reservation=reservation)
    return render(request, 'reservations/order_food.html', {
        'reservation': reservation,
        'categories': categories,
        'order': order,
    })


from django.http import JsonResponse

@login_required
def add_to_order(request, reservation_id, item_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    menu_item = get_object_or_404(MenuItem, id=item_id)
    order, created = Order.objects.get_or_create(reservation=reservation)
    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        menu_item=menu_item,
        defaults={'price': menu_item.price, 'quantity': 1}
    )
    if not created:
        order_item.quantity += 1
        order_item.save()
    return JsonResponse({'success': True})


@login_required
def remove_from_order(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id, order__reservation__user=request.user)
    order_item.delete()
    return JsonResponse({'success': True})


@login_required
def update_order_item(request, item_id, action):
    order_item = get_object_or_404(OrderItem, id=item_id, order__reservation__user=request.user)
    if action == 'increase':
        order_item.quantity += 1
    elif action == 'decrease' and order_item.quantity > 1:
        order_item.quantity -= 1
    order_item.save()
    return JsonResponse({'success': True})


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'reservations/profile.html', {'form': form})

@login_required
def remove_favorite(request, item_id):
    """Удаление из избранного"""
    Favorite.objects.filter(user=request.user, menu_item_id=item_id).delete()
    messages.success(request, 'Удалено из избранного')
    return redirect('my_reservations')


@login_required
def add_favorite(request, item_id):
    """Добавление/удаление из избранного"""
    menu_item = get_object_or_404(MenuItem, id=item_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, menu_item=menu_item)
    if not created:
        favorite.delete()
        messages.success(request, f'{menu_item.name} удалён из избранного')
    else:
        messages.success(request, f'{menu_item.name} добавлен в избранное')


    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', 'menu'))
    return redirect(next_url)

@login_required
def repeat_order(request, reservation_id):
    """Повторить заказ с возможностью изменения"""
    old_reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            new_reservation = form.save(commit=False)
            new_reservation.user = request.user
            new_reservation.save()

            # Копируем заказ
            if hasattr(old_reservation, 'order'):
                new_order = Order.objects.create(reservation=new_reservation)
                for item in old_reservation.order.items.all():
                    OrderItem.objects.create(
                        order=new_order,
                        menu_item=item.menu_item,
                        quantity=item.quantity,
                        price=item.menu_item.price
                    )

            messages.success(request, f'Создано новое бронирование №{new_reservation.user_number}!')
            return redirect('order_food', reservation_id=new_reservation.id)
    else:
        form = ReservationForm(initial={
            'date': old_reservation.date,
            'time': old_reservation.time,
            'guests_count': old_reservation.guests_count,
            'first_name': old_reservation.first_name,
            'last_name': old_reservation.last_name,
            'phone': old_reservation.phone,
        })

    return render(request, 'reservations/repeat_order.html', {
        'form': form,
        'old_reservation': old_reservation,
    })

def events(request):
    """Страница событий"""
    events = Event.objects.filter(is_active=True)
    return render(request, 'reservations/events.html', {'events': events})


def event_detail(request, event_id):
    """Детальная страница события"""
    event = get_object_or_404(Event, id=event_id, is_active=True)
    return render(request, 'reservations/event_detail.html', {'event': event})


from django.http import JsonResponse


@login_required
def cancel_reservation_ajax(request, pk):
    """Отмена бронирования через AJAX (модальное окно)"""
    if request.method == 'POST':
        try:
            reservation = Reservation.objects.get(pk=pk, user=request.user)

            if reservation.status == 'cancelled':
                return JsonResponse({'success': False, 'error': 'Бронирование уже отменено'})

            reservation.status = 'cancelled'
            reservation.save()

            return JsonResponse({'success': True})

        except Reservation.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Бронирование не найдено'}, status=404)

    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'}, status=400)


from django.http import JsonResponse


@login_required
def add_favorite_ajax(request, item_id):
    """Добавление/удаление из избранного через AJAX (без перезагрузки)"""
    menu_item = get_object_or_404(MenuItem, id=item_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, menu_item=menu_item)

    if not created:
        favorite.delete()
        is_favorite = False
    else:
        is_favorite = True

    return JsonResponse({
        'success': True,
        'is_favorite': is_favorite,
        'message': 'Добавлено в избранное' if is_favorite else 'Удалено из избранного'
    })


from django.http import JsonResponse


@login_required
def remove_favorite_ajax(request, item_id):
    """Удаление из избранного через AJAX (без перезагрузки)"""
    try:
        menu_item = get_object_or_404(MenuItem, id=item_id)
        deleted, _ = Favorite.objects.filter(user=request.user, menu_item=menu_item).delete()

        if deleted:
            return JsonResponse({'success': True, 'message': 'Удалено из избранного'})
        else:
            return JsonResponse({'success': False, 'error': 'Блюдо не найдено в избранном'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

