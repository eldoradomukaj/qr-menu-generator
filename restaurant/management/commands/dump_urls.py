from typing import Tuple

from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse

from restaurant.models import Restaurant, Category, Menu

class Command(BaseCommand):
    help = 'Outputs a list of URLs for the given restaurant ID.'

    def add_arguments(self, parser):
        parser.add_argument('restaurant_id', type=int)

    def handle(self, *args, **options):
        restaurant: Restaurant = Restaurant.objects.get(cust_pk=options['restaurant_id'])
        self.stdout.write('https://nomenu.io' + reverse('menu', args=(restaurant.cust_pk,)))
        self.stdout.write('https://nomenu.io' + reverse('favorites', args=(restaurant.cust_pk,)))

        categories: Tuple[Category] = Category.objects.filter(restaurant=restaurant)
        for category in categories:
            self.stdout.write('https://nomenu.io' + reverse('category', args=(restaurant.cust_pk,category.slug)))
            menus: Tuple[Menu] = Menu.objects.filter(category=category)
            for menu in menus:
                self.stdout.write('https://nomenu.io' + reverse('item', args=(restaurant.cust_pk,category.slug, menu.pk)))