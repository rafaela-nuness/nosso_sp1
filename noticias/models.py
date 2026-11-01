
from django.db import models


class Noticia(models.Model):
    STATUS_CHOICES = [
        ("rascunho", "Rascunho"),
        ("publicado", "Publicado"),
    ]

    REGIAO_CHOICES = [
        ("Centro", "Centro"),
        ("Zona Leste", "Zona Leste"),
        ("Zona Norte", "Zona Norte"),
        ("Zona Sul", "Zona Sul"),
        ("Zona Oeste", "Zona Oeste"),
    ]

    titulo = models.CharField(max_length=200)
    resumo = models.TextField()
    categoria = models.CharField(max_length=100)
    local = models.CharField(max_length=150, blank=True)
    regiao = models.CharField(
        max_length=50,
        choices=REGIAO_CHOICES,
        blank=True
    )
    imagem = models.URLField(blank=True)
    conteudo = models.TextField()
    tags = models.CharField(max_length=250, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="rascunho"
    )
    autor_email = models.EmailField(
        blank=True,
        default=""
    )
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


class Comentario(models.Model):
    noticia = models.ForeignKey(
        Noticia,
        on_delete=models.CASCADE,
        related_name="comentarios"
    )
    nome = models.CharField(max_length=100)
    autor_email = models.EmailField(
        blank=True,
        default=""
    )
    texto = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    aprovado = models.BooleanField(default=False)

    def __str__(self):
        return f"Comentário de {self.nome}"
