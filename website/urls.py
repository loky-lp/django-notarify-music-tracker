from django.urls import path

from . import views

app_name = "website"
urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout, name="logout"),
    path("populate_db/", views.populate_db, name="populate_db"),
]
