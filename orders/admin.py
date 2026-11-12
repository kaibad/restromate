from django.contrib import admin

from .models import Category, MenuItem, Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity", "is_reserved")
    list_editable = ("is_reserved",)
    list_filter = ("is_reserved",)
    search_fields = ("name",)
    ordering = ("name",)


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    fields = ("name", "price", "description")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "item_count")
    search_fields = ("name",)
    ordering = ("name",)
    inlines = [MenuItemInline]

    @admin.display(description="Items")
    def item_count(self, obj):
        return obj.items.count()


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price")
    list_filter = ("category",)
    list_select_related = ("category",)
    search_fields = ("name", "description", "category__name")
    ordering = ("category__name", "name")