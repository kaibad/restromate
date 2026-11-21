from django.shortcuts import redirect

from accounts.models import User

class HomeRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):



        # handle before  reaching to views
        if request.path == "/":
            user = request.user

            if not user.is_authenticated:
                return redirect("login_view_url")

            elif user.role == User.ROLES_CHOICES.WAITER:
                return redirect("tables_view_url")
            elif user.role == User.ROLES_CHOICES.KITCHEN:
                return redirect("kitchen_dashboard_view_url")
            elif user.role == User.ROLES_CHOICES.BILLING:
                return redirect("tables_for_billing_url")


        # Code executed before the view
        response = self.get_response(request)
        # Code executed after the view
        return response