import os
import django
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_delivery_project.settings')
django.setup()

from shop.models import Category, Product

# Сначала удалим старые товары (но оставим категории)
print("🗑️  Очищаем старые товары...")
Product.objects.all().delete()
print("✅ Товары очищены")

# ============================================
# 1. СОЗДАЁМ КАТЕГОРИИ (обновляем slug если пустой)
# ============================================
categories_data = [
    'Овощи и фрукты',
    'Молочные продукты',
    'Мясо и птица',
    'Рыба и морепродукты',
    'Хлеб и выпечка',
    'Бакалея',
    'Напитки',
    'Сладости и десерты',
    'Замороженные продукты',
    'Готовая еда',
]

print("\n📦 Обновляем категории...")
categories = {}
for cat_name in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_name,
        defaults={'slug': slugify(cat_name)}
    )
    # Если slug пустой - обновляем
    if not category.slug:
        category.slug = slugify(cat_name)
        category.save()
    categories[cat_name] = category
    print(f"  ✅ {category.name} -> {category.slug}")

# ============================================
# 2. СОЗДАЁМ ТОВАРЫ
# ============================================
products_data = [
    # Овощи и фрукты
    {'name': 'Яблоки', 'category': 'Овощи и фрукты', 'price': 150, 'stock': 50},
    {'name': 'Бананы', 'category': 'Овощи и фрукты', 'price': 200, 'stock': 30},
    {'name': 'Апельсины', 'category': 'Овощи и фрукты', 'price': 180, 'stock': 40},
    {'name': 'Картофель', 'category': 'Овощи и фрукты', 'price': 80, 'stock': 100},
    {'name': 'Морковь', 'category': 'Овощи и фрукты', 'price': 60, 'stock': 80},
    {'name': 'Лук репчатый', 'category': 'Овощи и фрукты', 'price': 50, 'stock': 90},
    {'name': 'Капуста', 'category': 'Овощи и фрукты', 'price': 70, 'stock': 60},
    {'name': 'Огурцы', 'category': 'Овощи и фрукты', 'price': 120, 'stock': 40},
    {'name': 'Помидоры', 'category': 'Овощи и фрукты', 'price': 160, 'stock': 35},
    {'name': 'Лимоны', 'category': 'Овощи и фрукты', 'price': 90, 'stock': 25},
    
    # Молочные продукты
    {'name': 'Молоко 1л', 'category': 'Молочные продукты', 'price': 120, 'stock': 50},
    {'name': 'Кефир 1л', 'category': 'Молочные продукты', 'price': 110, 'stock': 40},
    {'name': 'Сметана 200г', 'category': 'Молочные продукты', 'price': 80, 'stock': 45},
    {'name': 'Творог 200г', 'category': 'Молочные продукты', 'price': 150, 'stock': 30},
    {'name': 'Сыр 200г', 'category': 'Молочные продукты', 'price': 250, 'stock': 25},
    {'name': 'Масло сливочное', 'category': 'Молочные продукты', 'price': 180, 'stock': 35},
    {'name': 'Йогурт', 'category': 'Молочные продукты', 'price': 70, 'stock': 60},
    {'name': 'Ряженка', 'category': 'Молочные продукты', 'price': 90, 'stock': 30},
    
    # Мясо и птица
    {'name': 'Куриное филе', 'category': 'Мясо и птица', 'price': 350, 'stock': 40},
    {'name': 'Говядина', 'category': 'Мясо и птица', 'price': 550, 'stock': 20},
    {'name': 'Свинина', 'category': 'Мясо и птица', 'price': 450, 'stock': 25},
    {'name': 'Куриные крылья', 'category': 'Мясо и птица', 'price': 280, 'stock': 35},
    {'name': 'Фарш', 'category': 'Мясо и птица', 'price': 320, 'stock': 30},
    {'name': 'Котлеты куриные', 'category': 'Мясо и птица', 'price': 280, 'stock': 40},
    {'name': 'Колбаса вареная', 'category': 'Мясо и птица', 'price': 250, 'stock': 30},
    
    # Рыба и морепродукты
    {'name': 'Сёмга', 'category': 'Рыба и морепродукты', 'price': 800, 'stock': 15},
    {'name': 'Горбуша', 'category': 'Рыба и морепродукты', 'price': 450, 'stock': 20},
    {'name': 'Минтай', 'category': 'Рыба и морепродукты', 'price': 250, 'stock': 30},
    {'name': 'Креветки', 'category': 'Рыба и морепродукты', 'price': 600, 'stock': 15},
    {'name': 'Кальмары', 'category': 'Рыба и морепродукты', 'price': 350, 'stock': 20},
    {'name': 'Филе трески', 'category': 'Рыба и морепродукты', 'price': 380, 'stock': 25},
    
    # Хлеб и выпечка
    {'name': 'Хлеб белый', 'category': 'Хлеб и выпечка', 'price': 60, 'stock': 50},
    {'name': 'Хлеб чёрный', 'category': 'Хлеб и выпечка', 'price': 55, 'stock': 45},
    {'name': 'Батон нарезной', 'category': 'Хлеб и выпечка', 'price': 50, 'stock': 60},
    {'name': 'Лаваш', 'category': 'Хлеб и выпечка', 'price': 40, 'stock': 30},
    {'name': 'Плюшка', 'category': 'Хлеб и выпечка', 'price': 35, 'stock': 40},
    {'name': 'Кекс', 'category': 'Хлеб и выпечка', 'price': 80, 'stock': 25},
    
    # Бакалея
    {'name': 'Рис 1кг', 'category': 'Бакалея', 'price': 120, 'stock': 50},
    {'name': 'Гречка 1кг', 'category': 'Бакалея', 'price': 110, 'stock': 45},
    {'name': 'Макароны', 'category': 'Бакалея', 'price': 90, 'stock': 60},
    {'name': 'Мука 1кг', 'category': 'Бакалея', 'price': 80, 'stock': 40},
    {'name': 'Сахар 1кг', 'category': 'Бакалея', 'price': 70, 'stock': 50},
    {'name': 'Масло подсолнечное', 'category': 'Бакалея', 'price': 130, 'stock': 35},
    {'name': 'Крупа овсяная', 'category': 'Бакалея', 'price': 60, 'stock': 30},
    
    # Напитки
    {'name': 'Вода 1.5л', 'category': 'Напитки', 'price': 50, 'stock': 100},
    {'name': 'Сок апельсиновый', 'category': 'Напитки', 'price': 150, 'stock': 40},
    {'name': 'Чай чёрный', 'category': 'Напитки', 'price': 120, 'stock': 30},
    {'name': 'Кофе молотый', 'category': 'Напитки', 'price': 180, 'stock': 20},
    {'name': 'Лимонад', 'category': 'Напитки', 'price': 90, 'stock': 50},
    {'name': 'Квас', 'category': 'Напитки', 'price': 80, 'stock': 35},
    
    # Сладости
    {'name': 'Шоколад молочный', 'category': 'Сладости и десерты', 'price': 100, 'stock': 40},
    {'name': 'Конфеты', 'category': 'Сладости и десерты', 'price': 200, 'stock': 25},
    {'name': 'Печенье', 'category': 'Сладости и десерты', 'price': 70, 'stock': 45},
    {'name': 'Вафли', 'category': 'Сладости и десерты', 'price': 80, 'stock': 30},
    {'name': 'Зефир', 'category': 'Сладости и десерты', 'price': 90, 'stock': 25},
    {'name': 'Пирожное', 'category': 'Сладости и десерты', 'price': 60, 'stock': 35},
    
    # Заморозка
    {'name': 'Пельмени', 'category': 'Замороженные продукты', 'price': 280, 'stock': 30},
    {'name': 'Вареники', 'category': 'Замороженные продукты', 'price': 250, 'stock': 25},
    {'name': 'Мороженое', 'category': 'Замороженные продукты', 'price': 120, 'stock': 50},
    {'name': 'Овощная смесь', 'category': 'Замороженные продукты', 'price': 150, 'stock': 35},
    {'name': 'Блинчики', 'category': 'Замороженные продукты', 'price': 200, 'stock': 20},
    
    # Готовая еда
    {'name': 'Салат Цезарь', 'category': 'Готовая еда', 'price': 250, 'stock': 15},
    {'name': 'Салат Оливье', 'category': 'Готовая еда', 'price': 200, 'stock': 20},
    {'name': 'Суп куриный', 'category': 'Готовая еда', 'price': 180, 'stock': 15},
    {'name': 'Борщ', 'category': 'Готовая еда', 'price': 200, 'stock': 12},
    {'name': 'Котлета с гарниром', 'category': 'Готовая еда', 'price': 280, 'stock': 18},
]

print("\n📦 Создаём товары...")
created_count = 0
for product_data in products_data:
    category = categories.get(product_data['category'])
    if not category:
        print(f"  ❌ Категория не найдена: {product_data['category']}")
        continue
    
    product, created = Product.objects.get_or_create(
        name=product_data['name'],
        category=category,
        defaults={
            'slug': slugify(product_data['name']),
            'price': product_data['price'],
            'stock': product_data['stock'],
            'available': True
        }
    )
    if created:
        created_count += 1
        print(f"  ✅ {product.name} ({product.price} ₽)")

print(f"\n🎉 Готово! Создано товаров: {created_count}")
print(f"📊 Всего категорий: {len(categories)}")