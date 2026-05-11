from django.db import models
from django.contrib.auth.models import User


class Reservation(models.Model):
    """Бронирование"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Клиент")
    user_number = models.IntegerField(default=0, verbose_name="Номер брони у пользователя")
    first_name = models.CharField(max_length=50, verbose_name="Имя", default='')
    last_name = models.CharField(max_length=50, verbose_name="Фамилия", default='')
    date = models.DateField(verbose_name="Дата")
    time = models.CharField(max_length=5, verbose_name="Время")
    guests_count = models.IntegerField(verbose_name="Количество гостей")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ['-date', '-time']

    def __str__(self):
        return f"Бронь №{self.user_number} - {self.user.username} на {self.date} {self.time}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Только при создании нового бронирования
            last = Reservation.objects.filter(user=self.user).order_by('-user_number').first()
            self.user_number = (last.user_number + 1) if last else 1
        super().save(*args, **kwargs)

class MenuCategory(models.Model):
    """Категория меню"""
    name = models.CharField(max_length=100, verbose_name="Название категории")
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Категория меню"
        verbose_name_plural = "Категории меню"
        ordering = ['order']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """Блюдо в меню"""
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, verbose_name="Категория")
    name = models.CharField(max_length=200, verbose_name="Название блюда")
    description = models.TextField(blank=True, verbose_name="Описание")
    composition = models.TextField(blank=True, verbose_name="Состав")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    weight = models.CharField(max_length=50, blank=True, verbose_name="Вес/Объем")
    image = models.ImageField(upload_to='menu/', blank=True, null=True, verbose_name="Фото блюда")
    is_available = models.BooleanField(default=True, verbose_name="Доступно")

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} - {self.price} руб."


class Order(models.Model):
    """Заказ еды"""
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('cooking', 'Готовится'),
        ('ready', 'Готов'),
        ('completed', 'Завершён'),
    ]

    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='order', verbose_name="Бронирование")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class OrderItem(models.Model):
    """Позиция заказа"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, verbose_name="Блюдо")
    quantity = models.IntegerField(default=1, verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    @property
    def total_price(self):
        return self.price * self.quantity

class Favorite(models.Model):
    """Избранное блюдо"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, verbose_name="Блюдо")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        unique_together = ['user', 'menu_item']

    def __str__(self):
        return f"{self.user.username} - {self.menu_item.name}"

class Event(models.Model):
    """Событие ресторана"""
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    date = models.DateTimeField(verbose_name="Дата и время")
    image = models.ImageField(upload_to='events/', blank=True, null=True, verbose_name="Изображение")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"
        ordering = ['date']

    def __str__(self):
        return self.title