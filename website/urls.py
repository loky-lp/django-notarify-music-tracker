from django.urls import path

from . import views

app_name = "website"
urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout, name="logout"),
    path("populate_db/", views.populate_db, name="populate_db"),
    path("artist/<int:artist_id>/", views.artist_details, name="artist_details"),
    path("song/<int:song_id>/track", views.song_action, name="song_action"),
]
