from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(unique=True, blank=True, verbose_name="URL")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(unique=True, blank=True, verbose_name="URL")
    description = models.TextField(verbose_name="Описание", blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0, verbose_name="Остаток")
    available = models.BooleanField(default=True, verbose_name="В наличии")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Корзина {self.user.username}"
    
    def get_total(self):
        total = 0
        for item in self.items.all():
            total += item.get_total()
        return total
    
    def get_count(self):
        return self.items.count()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def get_total(self):
        return self.product.price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'В доставке'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменён'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    address = models.TextField(verbose_name="Адрес доставки")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Заказ #{self.id} - {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity} (Заказ #{self.order.id})"
    
    def get_total(self):
        return self.price * self.quantity
    
    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"