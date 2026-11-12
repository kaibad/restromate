# orders/management/commands/populate_menu.py
from django.core.management.base import BaseCommand
from django.db import transaction

from orders.data.basic_menu_items import RESTAURANT_MENU_ITEM
from orders.models import Category, MenuItem


def display_name(key):
    return key.replace("_", " ").title()


class Command(BaseCommand):
    help = "Populate basic menu categories and menu items"

    @transaction.atomic
    def handle(self, *args, **options):
        self.categories_created = 0
        self.items_created = 0
        self.items_updated = 0

        for category_key, content in RESTAURANT_MENU_ITEM.items():
            if isinstance(content, dict):
                # Nested group (e.g. drinks), one category per sub-group
                for sub_key, sub_items in content.items():
                    name = f"{display_name(category_key)} - {display_name(sub_key)}"
                    self.load_category(name, sub_items)
            else:
                self.load_category(display_name(category_key), content)

        self.stdout.write(
            self.style.SUCCESS(
                f"Done: {self.categories_created} categories created, "
                f"{self.items_created} items created, "
                f"{self.items_updated} items already existed (updated)."
            )
        )

    def load_category(self, name, items):
        category, created = Category.objects.get_or_create(name=name)
        if created:
            self.categories_created += 1

        for item in items:
            _, item_created = MenuItem.objects.update_or_create(
                category=category,
                name=item["name"],
                defaults={
                    "price": item["price"],
                    "description": item["description"],
                },
            )
            if item_created:
                self.items_created += 1
            else:
                self.items_updated += 1