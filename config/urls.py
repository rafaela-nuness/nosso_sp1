
from django.contrib import admin
from django.urls import path
from noticias import views

urlpatterns = [
    path("admin/", admin.site.urls),

    # PÁGINAS PÚBLICAS
    path("", views.home, name="home"),
    path("noticia/", views.noticia, name="noticia"),
    path("explorar/", views.explorar, name="explorar"),

    # LOGIN E CADASTRO
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("cadastro/", views.cadastro_leitor, name="cadastro_leitor"),

    # JORNALISTA
    path("painel/", views.painel, name="painel"),
    path("nova-noticia/", views.nova_noticia, name="nova_noticia"),
    path("minhas-publicacoes/", views.minhas_publicacoes, name="minhas_publicacoes"),

    # ADMINISTRADOR
    path("administracao/", views.administracao, name="administracao"),
    path("editar-noticia/<int:id>/", views.editar_noticia, name="editar_noticia"),
    path("excluir-noticia/<int:id>/", views.excluir_noticia, name="excluir_noticia"),
    path("comentarios/", views.comentarios, name="comentarios"),
    path(
        "moderar-comentario/<int:id>/<str:acao>/",
        views.moderar_comentario,
        name="moderar_comentario"
    ),

    # LEITOR
    path("leitor/", views.portal_leitor, name="portal_leitor"),
    path(
    "alternar-favorito/<int:id>/",
    views.alternar_favorito,
    name="alternar_favorito"
),
]
