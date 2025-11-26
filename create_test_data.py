import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flower_project.settings')
django.setup()

from catalog.models import Category, Product


def create_test_data():
    # Создаем категории
    categories_data = [
        {
            'name': 'Розы',
            'slug': 'roses',
            'description': 'Красивые и ароматные розы разных сортов'
        },
        {
            'name': 'Тюльпаны',
            'slug': 'tulips',
            'description': 'Яркие и нежные тюльпаны'
        },
        {
            'name': 'Хризантемы',
            'slug': 'chrysanthemums',
            'description': 'Пышные и долгостоящие хризантемы'
        },
        {
            'name': 'Свадебные букеты',
            'slug': 'wedding-bouquets',
            'description': 'Элегантные букеты для особого дня'
        }
    ]

    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults=cat_data
        )
        categories.append(category)
        print(f'Создана категория: {category.name}')

    # Создаем товары
    products_data = [
        {
            'name': 'Букет из красных роз',
            'slug': 'red-roses-bouquet',
            'description': 'Роскошный букет из 25 алых роз, идеально подходит для романтического подарка.',
            'price': 2500,
            'category': categories[0]
        },
        {
            'name': 'Букет из белых роз',
            'slug': 'white-roses-bouquet',
            'description': 'Элегантный букет из 15 белых роз, символ чистоты и невинности.',
            'price': 1800,
            'category': categories[0]
        },
        {
            'name': 'Тюльпаны микс',
            'slug': 'mixed-tulips',
            'description': 'Яркий букет из разноцветных тюльпанов, который подарит весеннее настроение.',
            'price': 1200,
            'category': categories[1]
        },
        {
            'name': 'Букет невесты',
            'slug': 'bridal-bouquet',
            'description': 'Изысканный свадебный букет из белых роз и хризантем.',
            'price': 3500,
            'category': categories[3]
        },
        {
            'name': 'Хризантемы солнечные',
            'slug': 'sunny-chrysanthemums',
            'description': 'Яркие желтые хризантемы, которые будут радовать вас долгое время.',
            'price': 900,
            'category': categories[2]
        }
    ]

    for prod_data in products_data:
        product, created = Product.objects.get_or_create(
            slug=prod_data['slug'],
            defaults=prod_data
        )
        print(f'Создан товар: {product.name} - {product.price} руб.')


if __name__ == '__main__':
    create_test_data()