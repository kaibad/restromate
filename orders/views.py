import json
from django.db import transaction
from django.db.models import Exists, OuterRef
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from accounts.models import User
from .decorators import role_required
from .models import Category, KitchenStation, MenuItem, Order, OrderItem, Table
from django.contrib import messages
from collections import defaultdict
from django.urls import reverse
from django.views.decorators.http import require_POST



def ready_items_for(table):
    """Items of this table that the kitchen finished and the waiter has not served yet."""
    return (
        OrderItem.objects.filter(order__table=table, status=OrderItem.ITEM_STATUS.READY)
        .select_related("menu_item", "order")
        .order_by("order__created_at")
    )


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
                       priority=menu_items[item_id].priority
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
    context = {
        "categories": Category.objects.prefetch_related("items"),
        "table": table,
        "table_id": table_id,
        "orders": orders,
        "unbilled_total": sum(order.total for order in orders),
        "ready_items": ready_items_for(table),
    }
    return render(request, "orders/menu.html", context)


@role_required([User.ROLES_CHOICES.KITCHEN])
def kitchen_dashboard_view(request):
    station_code = request.GET.get("station")  # e.g. /kitchen/?station=grill

    all_items = list(
        OrderItem.objects.filter(status=OrderItem.ITEM_STATUS.PREPARING)
        .select_related("menu_item__station", "order__table")
        .order_by("-priority", "order__created_at")
    )

    def code_of(item):
        station = item.menu_item.station
        return station.code if station else "none"

    # Sidebar: every station with items waiting, and its count (never filtered)
    stations = {}
    for item in all_items:
        station = item.menu_item.station
        entry = stations.setdefault(
            code_of(item),
            {
                "code": code_of(item),
                "name": station.name if station else "No station",
                "count": 0,
            },
        )
        entry["count"] += 1

    # Filter only if the code matches a station that has items waiting
    selected = stations.get(station_code) if station_code else None

    if selected:
        shown_items = [i for i in all_items if code_of(i) == selected["code"]]
    else:
        shown_items = all_items

    grouped_items = defaultdict(list)
    for item in shown_items:
        station = item.menu_item.station
        grouped_items[station.name if station else "No station"].append(item)

    context = {
        "order_items": dict(grouped_items),
        "stations": list(stations.values()),
        "selected_station": selected["code"] if selected else "",
        "selected_station_name": selected["name"] if selected else "",
        "total_items": len(shown_items),
        "high_priority_count": sum(
            1 for i in shown_items if i.priority == MenuItem.PRIORITY_CHOICES.HIGH
        ),
        "oldest_order_time": min((i.order.created_at for i in shown_items), default=None),
    }
    return render(request, "orders/kitchen-dashboard.html", context)


@role_required([User.ROLES_CHOICES.KITCHEN])
def kicthen_item_view(request, pk):
    order_item = get_object_or_404(
        OrderItem.objects.select_related("menu_item__station"), pk=pk
    )

    if request.method == "POST":
        if order_item.status == OrderItem.ITEM_STATUS.PREPARING:
            order_item.status = OrderItem.ITEM_STATUS.READY
            order_item.save()  # save(), so your signals run
            messages.success(request, f"{order_item.menu_item.name} marked as ready.")
        else:
            status_label = OrderItem.ITEM_STATUS(order_item.status).label.lower()
            messages.warning(request, f"{order_item.menu_item.name} is already {status_label}.")

        # Go back to the board for this item's station
        station = order_item.menu_item.station
        station_code = station.code if station else "none"
        return redirect(f"{reverse('kitchen_dashboard_view_url')}?station={station_code}")

    return render(request, "orders/kicthen_item.html", {"order_item": order_item})

@role_required([User.ROLES_CHOICES.WAITER])
def tables_status_live(request):
    ready_items = OrderItem.objects.filter(
        order__table=OuterRef("pk"),
        status=OrderItem.ITEM_STATUS.READY
    )

    tables = Table.objects.filter(
        Exists(ready_items)
    )

    table_ids = list(
        tables.values_list("id", flat=True)
    )

    # print([tables])

    return JsonResponse({
        "table_ids": table_ids,
    })


@role_required([User.ROLES_CHOICES.WAITER])
def ready_items_partial(request, table_id):
    """Only the 'ready to serve' box. The menu page polls this to stay up to date."""
    table = get_object_or_404(Table, id=table_id)
    return render(request, "orders/_ready_items.html", {"ready_items": ready_items_for(table)})


@role_required([User.ROLES_CHOICES.WAITER])
@require_POST
def serve_item_view(request):
    item_id = request.POST.get("item_id", "")
    if not item_id.isdigit():
        return HttpResponseBadRequest("Invalid item.")

    item = get_object_or_404(
        OrderItem.objects.select_related("menu_item", "order"), pk=int(item_id)
    )

    # Only ready -> served is allowed from here
    if item.status == OrderItem.ITEM_STATUS.READY:
        item.status = OrderItem.ITEM_STATUS.SERVED
        item.save()  # save(), so the order-status signal runs
        messages.success(request, f"{item.menu_item.name} marked as served.")
    else:
        label = OrderItem.ITEM_STATUS(item.status).label.lower()
        messages.warning(request, f"{item.menu_item.name} is {label}, so it can't be served from here.")

    return redirect("menu_view_url", table_id=item.order.table_id) # type: ignore


@role_required([User.ROLES_CHOICES.BILLING])
def tables_for_billing(request):
    tables = Table.objects.all()

    available_count = tables.filter(is_reserved=False).count()
    occupied_count = tables.filter(is_reserved=True).count()

    return render(request, "orders/tables-for-billing.html", {
        "tables": tables,
        "available_count": available_count,
        "occupied_count": occupied_count,
    })


@role_required([User.ROLES_CHOICES.BILLING])
def billing_tables_status_live(request):

    all_tables = Order.objects.values_list(
        'table_id', flat=True
    ).distinct()

    table_ids = []

    for table_id in all_tables:
        orders = Order.objects.filter(table_id=table_id)

        if not orders.exclude(
            status=Order.ORDER_STATUS.SERVED
        ).exists():
            table_ids.append(str(table_id))

    return JsonResponse({
        "table_ids": table_ids,
    })
