from django.urls import path

from . import views

app_name = "about"

urlpatterns = [
    path("author/", views.AuthorStaticPage.as_view(), name="author"),
    path("tech/", views.TechStaticPage.as_view(), name="tech"),
]
