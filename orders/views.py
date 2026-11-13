import json

from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from .decorators import role_required
from .models import Category, MenuItem, Order, OrderItem, Table
from django.contrib import messages


@role_required([User.ROLES_CHOICES.WAITER])
def tables_view(request):
    tables = Table.objects.all()
    context = {
        "tables": tables,
        "available_count": tables.filter(is_reserved=False).count(),
        "occupied_count": tables.filter(is_reserved=True).count(),
    }
    return render(request, "orders/tables.html", context)


@role_required([User.ROLES_CHOICES.WAITER])
def menu_view(request, table_id):
    table = get_object_or_404(Table, id=table_id)

    if request.method == "POST":
        try:
            order_items = json.loads(request.POST.get("order-items", "[]"))
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid order data.")

        if not isinstance(order_items, list) or not order_items:
            return HttpResponseBadRequest("No items in the order.")

        # Validate the payload and load all menu items in one query
        try:
            # This is a dict comprehension. It converts the list from the browser into a dict that maps item id to quantity.
            wanted = {int(e["item_id"]): int(e["quantity"]) for e in order_items} #wanted = {1: 2, 6: 1}
            # wanted = {}
            # for e in order_items:
            #      wanted[int(e["item_id"])] = int(e["quantity"])
        except (KeyError, TypeError, ValueError):
            return HttpResponseBadRequest("Invalid order items.")

        if any(qty < 1 for qty in wanted.values()):
            return HttpResponseBadRequest("Quantities must be at least 1.")
        
        # in_bulk fetches many objects in a single query and returns a dict keyed by primary key: {1: <MenuItem: Momo>, 6: <MenuItem: Tea>}
        menu_items = MenuItem.objects.in_bulk(wanted.keys())
        if len(menu_items) != len(wanted):
            return HttpResponseBadRequest("One or more menu items do not exist.")

        with transaction.atomic():
            order = Order.objects.create(table=table)
            OrderItem.objects.bulk_create(
                [
                    OrderItem(
                        order=order,
                        menu_item=menu_items[item_id],
                        price=menu_items[item_id].price,  # price at order time
                        quantity=qty,
                    )
                    for item_id, qty in wanted.items()
                ]
            )
            if not table.is_reserved:
                table.is_reserved = True
                table.save(update_fields=["is_reserved"])

        messages.success(request, f"Order placed for {table.name}.")
        return redirect("tables_view_url")

    orders = (
        Order.objects.filter(table=table)
        .exclude(status=Order.ORDER_STATUS.BILLED)
        .prefetch_related("items__menu_item")
        .order_by("-created_at")
    )
    # print(f"order {orders}")
    context = {
        "categories": Category.objects.prefetch_related("items"),
        "table": table,
        "table_id": table_id,
        "orders": orders,
        "unbilled_total": sum(order.total for order in orders),
    }
    return render(request, "orders/menu.html", context)