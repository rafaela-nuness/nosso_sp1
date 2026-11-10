
from django.contrib import admin
from .models import Noticia, Comentario, Leitor, SolicitacaoJornalista


@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria", "regiao", "status", "data_criacao")
    list_filter = ("status", "categoria", "regiao")
    search_fields = ("titulo", "resumo")


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ("nome", "noticia", "data_criacao", "aprovado")
    list_filter = ("aprovado", "data_criacao")
    search_fields = ("nome", "texto")
    list_editable = ("aprovado",)


@admin.register(Leitor)
class LeitorAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "jornalista", "data_criacao")
    search_fields = ("nome", "email")


@admin.register(SolicitacaoJornalista)
class SolicitacaoJornalistaAdmin(admin.ModelAdmin):
    list_display = ("nome_completo", "leitor", "zona", "bairro", "status", "data_criacao")
    list_filter = ("status",)
