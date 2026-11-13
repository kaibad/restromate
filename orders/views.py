from django.shortcuts import render,redirect
from .decorators import role_required
from accounts.models import User
from .models import Table,Category,MenuItem
import json


# Create your views here.
# @role_required(['w'])
@role_required([User.ROLES_CHOICES.WAITER])
def tables_view(request):
    tables = Table.objects.all()
    context = {
        'tables': tables,
        'available_count': tables.filter(is_reserved=False).count(),
        'occupied_count': tables.filter(is_reserved=True).count(),
    }

    return render(request,"orders/tables.html",context)

@role_required([User.ROLES_CHOICES.WAITER])
def menu_view(request,table_id):

    categories = Category.objects.all()

    if request.method == "POST":
        order_items = json.loads(request.POST.get("order-items", "{}"))
        # print(order_items, type(order_items))

        for entry in order_items:
            item = MenuItem.objects.get(id=entry["item_id"])
            print(item.name, entry["quantity"], item.price * entry["quantity"])

        return redirect("tables_view_url")


    context = {
            'categories': categories,
            "table_id": table_id
        }

    return render(request,"orders/menu.html",context)


