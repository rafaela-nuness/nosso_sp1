
from django.contrib import admin
from django.urls import path
from noticias import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("login/", views.login, name="login"),
    path("noticia/", views.noticia, name="noticia"),
    path("painel/", views.painel, name="painel"),
    path("nova-noticia/", views.nova_noticia, name="nova_noticia"),
    path("explorar/", views.explorar, name="explorar"),
]
