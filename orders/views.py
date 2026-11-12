from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from accounts.models import User

# Create your views here.
# @role_required(['w'])
@role_required([User.ROLES_CHOICES.WAITER])
def tables_view(request):
    return render(request,"orders/tables.html")