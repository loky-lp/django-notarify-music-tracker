from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt


@login_required(login_url="/login")
def index(request):
    return HttpResponse("Hello, world. You're at the website index.")


@csrf_exempt  # DISABLED ONLY FOR DEMONSTRATION PURPOSES, in production environments the CSRF check MUST be activated
def login(request):
    if request.user.is_authenticated:
        return redirect("website:index")

    match request.method:
        case "GET":
            return render(request, "website/login.html")
        case "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                django_login(request, user)
                return redirect("website:index")
            else:
                context = {'error': "Credenziali non valide"}
                return render(request, "website/login.html", context)
        case _:
            return HttpResponseNotAllowed(HttpResponse("Method not valid"))


@csrf_exempt
def signup(request):
    if request.user.is_authenticated:
        return redirect("website:index")

    return render(request, 'website/signup.html')


@csrf_exempt
def logout(request):
    if not request.user.is_authenticated:
        return redirect("website:index")

    match request.method:
        case "POST":
            django_logout(request)
            return redirect("website:index")
        case _:
            return HttpResponseNotAllowed(HttpResponse("Method not valid"))
