from django.shortcuts import render
from .decorators import role_required
from accounts.models import User
from .models import Table,Category

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
    context = {
            'categories': categories,
            "table_id": table_id
        }

    return render(request,"orders/menu.html",context)


