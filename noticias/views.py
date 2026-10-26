
from django.shortcuts import render


def home(request):
    return render(request, "noticias/home.html")


def login(request):
    return render(request, "noticias/login.html")


def noticia(request):
    return render(request, "noticias/noticia.html")


def painel(request):
    return render(request, "noticias/painel.html")


def nova_noticia(request):
    return render(request, "noticias/nova_noticia.html")


def explorar(request):
    return render(request, "noticias/explorar.html")
