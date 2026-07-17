from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin import AdminSite
from django.contrib import messages
from .models import Category, Product, Cart, CartItem, Order, OrderItem


class CustomAdminSite(AdminSite):
    site_header = '🍕 Доставка продуктов - Админка'
    site_title = 'Админка магазина'
    index_title = 'Управление магазином'


admin_site = CustomAdminSite(name='myadmin')


@admin.register(Category, site=admin_site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'products_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def products_count(self, obj):
        count = obj.products.count()
        return format_html('<span style="background:#28a745;color:white;padding:2px 10px;border-radius:12px;font-size:12px;">{}</span>', count)
    products_count.short_description = "Товаров"


@admin.register(Product, site=admin_site)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'available', 'image_preview']
    list_filter = ['category', 'available']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'available']
    list_per_page = 25
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:8px;border:2px solid #dee2e6;" />', obj.image.url)
        return "📷 Нет фото"
    image_preview.short_description = "Фото"


@admin.register(Cart, site=admin_site)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'items_count', 'total_sum']
    search_fields = ['user__username']
    readonly_fields = ['created_at']
    list_per_page = 20
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = "Товаров"
    
    def total_sum(self, obj):
        return format_html('<b style="color:#ff6b35;">{} ₽</b>', obj.get_total())
    total_sum.short_description = "Сумма"


@admin.register(CartItem, site=admin_site)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'quantity', 'total']
    search_fields = ['product__name', 'cart__user__username']
    list_per_page = 20
    
    def total(self, obj):
        return format_html('<b>{} ₽</b>', obj.get_total())
    total.short_description = "Сумма"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']
    can_delete = False
    fields = ['product', 'quantity', 'price']
    classes = ['collapse']
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order, site=admin_site)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status_badge', 'total', 'phone', 'items_count', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'phone', 'address']
    readonly_fields = ['total', 'created_at']
    fields = ['user', 'status', 'total', 'address', 'phone', 'comment', 'created_at']
    inlines = [OrderItemInline]
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_completed', 'mark_as_cancelled', 'send_test_push']
    
    def status_badge(self, obj):
        colors = {
            'new': '#6c757d',
            'processing': '#007bff',
            'shipped': '#ffc107',
            'completed': '#28a745',
            'cancelled': '#dc3545',
        }
        emojis = {
            'new': '🆕',
            'processing': '🔄',
            'shipped': '🚚',
            'completed': '✅',
            'cancelled': '❌',
        }
        return format_html(
            '<span style="background:{};color:{};padding:4px 14px;border-radius:20px;font-size:12px;font-weight:600;">{} {}</span>',
            colors.get(obj.status, '#6c757d'),
            'white' if obj.status != 'shipped' else '#1a1a2e',
            emojis.get(obj.status, ''),
            obj.get_status_display()
        )
    status_badge.short_description = "Статус"
    
    def items_count(self, obj):
        count = obj.items.count()
        return format_html('<span style="background:#ff6b35;color:white;padding:2px 10px;border-radius:12px;font-size:12px;">📦 {}</span>', count)
    items_count.short_description = "Товаров"
    
    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
    mark_as_processing.short_description = "🔄 В обработку"
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
    mark_as_shipped.short_description = "🚚 В доставку"
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "✅ Выполнено"
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_as_cancelled.short_description = "❌ Отменено"
    
    def send_test_push(self, request, queryset):
        from .views import send_push_notification
        count = 0
        for order in queryset:
            send_push_notification(order)
            count += 1
        self.message_user(request, f'✅ Push-уведомления отправлены для {count} заказов')
    send_test_push.short_description = "📨 Отправить push-уведомление"