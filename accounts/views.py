from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, get_user_model,login,logout
from django.contrib import messages

# User = get_user_model()

# messages.success() – Successful operations.

# messages.error() – Failed operations.

# messages.warning() – Warning messages.

# messages.info() – Informational messages.

# messages.debug() – Debug messages.

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember-me")

        print("Username:", username)
        # print("User exists:", User.objects.filter(username=username).exists())

        user = authenticate(
            request,
            username=username,
            password=password
        )

        # print("Authenticated user:", user)

        if user is not None:
            login(request,user)
            messages.success(request,"Login Sucessful")
            if remember_me is None:
                request.session.set_expiry(0)
            return redirect("tables_view_url")
        else:
            messages.error(request,"Invalid Credentials")
            return redirect("login_view_url")


    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect("login_view_url")