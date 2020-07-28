from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:name>", views.display_entries, name="display_entries"),
    path("create/", views.create, name="create"),
    path("search/", views.search_entries, name="search"),
    path("edit/<str:name>", views.edit, name="edit"),
    path("random/", views.random_page, name="random")
]
