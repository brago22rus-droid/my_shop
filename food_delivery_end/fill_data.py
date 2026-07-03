import os
import django
from django.utils.text import slugify

# Настройка Django окружения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_delivery_project.settings')
django.setup()

from shop.models import Category, Product

# ============================================
# 1. СОЗДАЁМ КАТЕГОРИИ
# ============================================
categories_data = [
    {'name': 'Овощи и фрукты'},
    {'name': 'Молочные продукты'},
    {'name': 'Мясо и птица'},
    {'name': 'Рыба и морепродукты'},
    {'name': 'Хлеб и выпечка'},
    {'name': 'Бакалея'},
    {'name': 'Напитки'},
    {'name': 'Сладости и десерты'},
    {'name': 'Замороженные продукты'},
    {'name': 'Готовая еда'},
]

print("📦 Создаём категории...")
categories = {}
for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'slug': slugify(cat_data['name'])}
    )
    categories[cat_data['name']] = category
    if created:
        print(f"  ✅ Создана категория: {category.name}")
    else:
        print(f"  ⏳ Категория уже существует: {category.name}")

# ============================================
# 2. СОЗДАЁМ ТОВАРЫ
# ============================================
products_data = [
    # Овощи и фрукты
    {'name': 'Яблоки', 'category': 'Овощи и фрукты', 'price': 150, 'stock': 50, 'description': 'Свежие яблоки, сорт "Голден"'},
    {'name': 'Бананы', 'category': 'Овощи и фрукты', 'price': 200, 'stock': 30, 'description': 'Спелые бананы из Эквадора'},
    {'name': 'Апельсины', 'category': 'Овощи и фрукты', 'price': 180, 'stock': 40, 'description': 'Сочные апельсины'},
    {'name': 'Картофель', 'category': 'Овощи и фрукты', 'price': 80, 'stock': 100, 'description': 'Молодой картофель'},
    {'name': 'Морковь', 'category': 'Овощи и фрукты', 'price': 60, 'stock': 80, 'description': 'Свежая морковь'},
    {'name': 'Лук репчатый', 'category': 'Овощи и фрукты', 'price': 50, 'stock': 90, 'description': 'Репчатый лук'},
    {'name': 'Капуста', 'category': 'Овощи и фрукты', 'price': 70, 'stock': 60, 'description': 'Белокочанная капуста'},
    {'name': 'Огурцы', 'category': 'Овощи и фрукты', 'price': 120, 'stock': 40, 'description': 'Свежие огурцы'},
    {'name': 'Помидоры', 'category': 'Овощи и фрукты', 'price': 160, 'stock': 35, 'description': 'Спелые помидоры'},
    {'name': 'Лимоны', 'category': 'Овощи и фрукты', 'price': 90, 'stock': 25, 'description': 'Свежие лимоны'},
    
    # Молочные продукты
    {'name': 'Молоко 1л 3.2%', 'category': 'Молочные продукты', 'price': 120, 'stock': 50, 'description': 'Пастеризованное молоко'},
    {'name': 'Кефир 1л', 'category': 'Молочные продукты', 'price': 110, 'stock': 40, 'description': 'Кефир 2.5% жирности'},
    {'name': 'Сметана 200г', 'category': 'Молочные продукты', 'price': 80, 'stock': 45, 'description': 'Сметана 20%'},
    {'name': 'Творог 200г', 'category': 'Молочные продукты', 'price': 150, 'stock': 30, 'description': 'Творог 9%'},
    {'name': 'Сыр "Российский" 200г', 'category': 'Молочные продукты', 'price': 250, 'stock': 25, 'description': 'Сыр полутвёрдый'},
    {'name': 'Масло сливочное 180г', 'category': 'Молочные продукты', 'price': 180, 'stock': 35, 'description': 'Сливочное масло 82.5%'},
    {'name': 'Йогурт 150г', 'category': 'Молочные продукты', 'price': 70, 'stock': 60, 'description': 'Питьевой йогурт'},
    {'name': 'Ряженка 500мл', 'category': 'Молочные продукты', 'price': 90, 'stock': 30, 'description': 'Ряженка 4%'},
    
    # Мясо и птица
    {'name': 'Куриное филе', 'category': 'Мясо и птица', 'price': 350, 'stock': 40, 'description': 'Куриная грудка охлаждённая'},
    {'name': 'Говядина', 'category': 'Мясо и птица', 'price': 550, 'stock': 20, 'description': 'Говядина вырезка'},
    {'name': 'Свинина', 'category': 'Мясо и птица', 'price': 450, 'stock': 25, 'description': 'Свинина корейка'},
    {'name': 'Куриные крылья', 'category': 'Мясо и птица', 'price': 280, 'stock': 35, 'description': 'Куриные крылья'},
    {'name': 'Фарш свино-говяжий', 'category': 'Мясо и птица', 'price': 320, 'stock': 30, 'description': 'Домашний фарш'},
    {'name': 'Котлеты куриные', 'category': 'Мясо и птица', 'price': 280, 'stock': 40, 'description': 'Куриные котлеты'},
    {'name': 'Колбаса вареная', 'category': 'Мясо и птица', 'price': 250, 'stock': 30, 'description': 'Варёная колбаса'},
    
    # Рыба и морепродукты
    {'name': 'Сёмга', 'category': 'Рыба и морепродукты', 'price': 800, 'stock': 15, 'description': 'Сёмга охлаждённая'},
    {'name': 'Горбуша', 'category': 'Рыба и морепродукты', 'price': 450, 'stock': 20, 'description': 'Горбуша свежая'},
    {'name': 'Минтай', 'category': 'Рыба и морепродукты', 'price': 250, 'stock': 30, 'description': 'Минтай филе'},
    {'name': 'Креветки', 'category': 'Рыба и морепродукты', 'price': 600, 'stock': 15, 'description': 'Креветки королевские'},
    {'name': 'Кальмары', 'category': 'Рыба и морепродукты', 'price': 350, 'stock': 20, 'description': 'Кальмары свежие'},
    {'name': 'Филе трески', 'category': 'Рыба и морепродукты', 'price': 380, 'stock': 25, 'description': 'Филе трески'},
    
    # Хлеб и выпечка
    {'name': 'Хлеб белый', 'category': 'Хлеб и выпечка', 'price': 60, 'stock': 50, 'description': 'Хлеб пшеничный'},
    {'name': 'Хлеб чёрный', 'category': 'Хлеб и выпечка', 'price': 55, 'stock': 45, 'description': 'Хлеб ржаной'},
    {'name': 'Батон нарезной', 'category': 'Хлеб и выпечка', 'price': 50, 'stock': 60, 'description': 'Батон нарезной'},
    {'name': 'Лаваш армянский', 'category': 'Хлеб и выпечка', 'price': 40, 'stock': 30, 'description': 'Тонкий лаваш'},
    {'name': 'Плюшка с маком', 'category': 'Хлеб и выпечка', 'price': 35, 'stock': 40, 'description': 'Сдобная плюшка'},
    {'name': 'Кекс', 'category': 'Хлеб и выпечка', 'price': 80, 'stock': 25, 'description': 'Кекс с изюмом'},
    
    # Бакалея
    {'name': 'Рис 1кг', 'category': 'Бакалея', 'price': 120, 'stock': 50, 'description': 'Рис круглозёрный'},
    {'name': 'Гречка 1кг', 'category': 'Бакалея', 'price': 110, 'stock': 45, 'description': 'Гречка ядрица'},
    {'name': 'Макароны 800г', 'category': 'Бакалея', 'price': 90, 'stock': 60, 'description': 'Макароны из твёрдых сортов'},
    {'name': 'Мука 1кг', 'category': 'Бакалея', 'price': 80, 'stock': 40, 'description': 'Мука пшеничная'},
    {'name': 'Сахар 1кг', 'category': 'Бакалея', 'price': 70, 'stock': 50, 'description': 'Сахарный песок'},
    {'name': 'Масло подсолнечное 1л', 'category': 'Бакалея', 'price': 130, 'stock': 35, 'description': 'Подсолнечное масло'},
    {'name': 'Крупа овсяная', 'category': 'Бакалея', 'price': 60, 'stock': 30, 'description': 'Овсяные хлопья'},
    
    # Напитки
    {'name': 'Вода 1.5л', 'category': 'Напитки', 'price': 50, 'stock': 100, 'description': 'Питьевая вода'},
    {'name': 'Сок апельсиновый 1л', 'category': 'Напитки', 'price': 150, 'stock': 40, 'description': 'Апельсиновый сок'},
    {'name': 'Чай чёрный 100г', 'category': 'Напитки', 'price': 120, 'stock': 30, 'description': 'Чай чёрный листовой'},
    {'name': 'Кофе молотый 100г', 'category': 'Напитки', 'price': 180, 'stock': 20, 'description': 'Кофе молотый'},
    {'name': 'Лимонад 1.5л', 'category': 'Напитки', 'price': 90, 'stock': 50, 'description': 'Лимонад газированный'},
    {'name': 'Квас 1.5л', 'category': 'Напитки', 'price': 80, 'stock': 35, 'description': 'Квас хлебный'},
    
    # Сладости и десерты
    {'name': 'Шоколад молочный', 'category': 'Сладости и десерты', 'price': 100, 'stock': 40, 'description': 'Молочный шоколад'},
    {'name': 'Конфеты 200г', 'category': 'Сладости и десерты', 'price': 200, 'stock': 25, 'description': 'Ассорти конфет'},
    {'name': 'Печенье', 'category': 'Сладости и десерты', 'price': 70, 'stock': 45, 'description': 'Печенье песочное'},
    {'name': 'Вафли', 'category': 'Сладости и десерты', 'price': 80, 'stock': 30, 'description': 'Вафли шоколадные'},
    {'name': 'Зефир', 'category': 'Сладости и десерты', 'price': 90, 'stock': 25, 'description': 'Зефир ванильный'},
    {'name': 'Пирожное', 'category': 'Сладости и десерты', 'price': 60, 'stock': 35, 'description': 'Пирожное бисквитное'},
    
    # Замороженные продукты
    {'name': 'Пельмени 800г', 'category': 'Замороженные продукты', 'price': 280, 'stock': 30, 'description': 'Пельмени с мясом'},
    {'name': 'Вареники 800г', 'category': 'Замороженные продукты', 'price': 250, 'stock': 25, 'description': 'Вареники с картошкой'},
    {'name': 'Мороженое', 'category': 'Замороженные продукты', 'price': 120, 'stock': 50, 'description': 'Мороженое пломбир'},
    {'name': 'Овощная смесь 400г', 'category': 'Замороженные продукты', 'price': 150, 'stock': 35, 'description': 'Смесь овощная'},
    {'name': 'Блинчики 500г', 'category': 'Замороженные продукты', 'price': 200, 'stock': 20, 'description': 'Блинчики с мясом'},
    
    # Готовая еда
    {'name': 'Салат "Цезарь"', 'category': 'Готовая еда', 'price': 250, 'stock': 15, 'description': 'Салат Цезарь с курицей'},
    {'name': 'Салат "Оливье"', 'category': 'Готовая еда', 'price': 200, 'stock': 20, 'description': 'Салат Оливье'},
    {'name': 'Суп куриный 500мл', 'category': 'Готовая еда', 'price': 180, 'stock': 15, 'description': 'Куриный суп'},
    {'name': 'Борщ 500мл', 'category': 'Готовая еда', 'price': 200, 'stock': 12, 'description': 'Борщ украинский'},
    {'name': 'Котлета с гарниром', 'category': 'Готовая еда', 'price': 280, 'stock': 18, 'description': 'Котлета с картофельным пюре'},
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
            'description': product_data.get('description', ''),
            'price': product_data['price'],
            'stock': product_data['stock'],
            'available': True
        }
    )
    if created:
        created_count += 1
        print(f"  ✅ Создан товар: {product.name} ({product.price} ₽)")
    else:
        print(f"  ⏳ Товар уже существует: {product.name}")

print(f"\n🎉 Готово! Создано категорий: {len(categories)}")
print(f"🎉 Создано товаров: {created_count}")