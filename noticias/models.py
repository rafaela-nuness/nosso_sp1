
from django.db import models


class Noticia(models.Model):
    STATUS_CHOICES = [
        ("rascunho", "Rascunho"),
        ("pendente", "Aguardando aprovação"),
        ("publicado", "Aceita"),
        ("negado", "Negada"),
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
    bairro = models.CharField(max_length=100, blank=True, default="")
    rua = models.CharField(max_length=150, blank=True, default="")
    regiao = models.CharField(
        max_length=50,
        choices=REGIAO_CHOICES,
        blank=True
    )
    imagem = models.URLField(blank=True)
    foto = models.FileField(upload_to="noticias/", blank=True)
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

    @property
    def imagem_url(self):
        """Foto enviada do computador (prioridade) ou link de imagem."""
        if self.foto:
            return self.foto.url
        return self.imagem

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
    aprovado = models.BooleanField(default=True)

    def __str__(self):
        return f"Comentário de {self.nome}"


class Leitor(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=128)
    jornalista = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class SolicitacaoJornalista(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Aguardando análise"),
        ("entrevista", "Entrevista marcada"),
        ("aceita", "Aceita"),
        ("recusada", "Recusada"),
    ]

    leitor = models.ForeignKey(
        Leitor,
        on_delete=models.CASCADE,
        related_name="solicitacoes"
    )
    nome_completo = models.CharField(max_length=150, blank=True, default="")
    cpf = models.CharField(max_length=14, blank=True, default="")
    zona = models.CharField(max_length=50, blank=True, default="")
    bairro = models.CharField(max_length=100, blank=True, default="")
    capacidades = models.TextField()  # habilidades do candidato
    experiencia = models.TextField(blank=True)
    curriculo = models.FileField(upload_to="curriculos/", blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pendente"
    )
    data_entrevista = models.DateTimeField(null=True, blank=True)
    detalhes_entrevista = models.CharField(max_length=250, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Solicitação de {self.leitor.nome}"


class CertificadoSolicitacao(models.Model):
    solicitacao = models.ForeignKey(
        SolicitacaoJornalista,
        on_delete=models.CASCADE,
        related_name="certificados"
    )
    imagem = models.FileField(upload_to="certificados/")

    def __str__(self):
        return f"Certificado de {self.solicitacao.leitor.nome}"
