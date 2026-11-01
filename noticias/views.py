
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Noticia, Comentario


# LOGINS TEMPORÁRIOS PARA TESTES
EMAIL_JORNALISTA = "jornalista@nossoSP.com"
SENHA_JORNALISTA = "NossoSP123!"

EMAIL_ADMIN = "admin@teste.com"
SENHA_ADMIN = "admin123"

EMAIL_LEITOR = "leitor@nossoSP.com"
SENHA_LEITOR = "Leitor123!"


# VERIFICAÇÃO DE PERMISSÕES
def usuario_logado(request):
    return request.session.get("usuario_tipo") in [
        "jornalista",
        "administrador"
    ]


def eh_jornalista(request):
    return request.session.get("usuario_tipo") == "jornalista"


def eh_administrador(request):
    return request.session.get("usuario_tipo") == "administrador"


def eh_leitor(request):
    return request.session.get("usuario_tipo") == "leitor"


def redirecionar_painel(request):
    if eh_administrador(request):
        return redirect("administracao")

    return redirect("painel")


# PÁGINA INICIAL
def home(request):
    publicacoes = Noticia.objects.filter(
        status="publicado"
    ).order_by("-data_criacao")

    return render(
        request,
        "noticias/home.html",
        {"publicacoes": publicacoes}
    )


# LOGIN
def login(request):
    erro = ""

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        senha = request.POST.get("senha", "")

        request.session.flush()

        if email == EMAIL_JORNALISTA and senha == SENHA_JORNALISTA:
            request.session["usuario_tipo"] = "jornalista"
            request.session["usuario_email"] = email
            return redirect("painel")

        elif email == EMAIL_ADMIN and senha == SENHA_ADMIN:
            request.session["usuario_tipo"] = "administrador"
            request.session["usuario_email"] = email
            return redirect("administracao")

        elif email == EMAIL_LEITOR and senha == SENHA_LEITOR:
            request.session["usuario_tipo"] = "leitor"
            request.session["usuario_email"] = email
            return redirect("portal_leitor")

        erro = "E-mail ou senha incorretos."

    return render(
        request,
        "noticias/login.html",
        {"erro": erro}
    )


# LOGOUT
def logout(request):
    request.session.flush()
    return redirect("login")


# DETALHES DA NOTÍCIA E COMENTÁRIOS
def noticia(request):
    publicacao_id = request.GET.get("id")

    publicacao = get_object_or_404(
        Noticia,
        id=publicacao_id,
        status="publicado"
    )

    erro_comentario = ""

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        texto = request.POST.get("comentario", "").strip()

        if not nome or not texto:
            erro_comentario = "Preencha seu nome e seu comentário."

        elif len(nome) > 100:
            erro_comentario = "O nome deve ter no máximo 100 caracteres."

        else:
            email_autor = ""

            if eh_leitor(request):
                email_autor = request.session.get("usuario_email", "")

            Comentario.objects.create(
                noticia=publicacao,
                nome=nome,
                autor_email=email_autor,
                texto=texto,
                aprovado=False
            )

            return redirect(
                f"/noticia/?id={publicacao.id}&enviado=1"
            )

    comentarios_publicados = Comentario.objects.filter(
        noticia=publicacao,
        aprovado=True
    ).order_by("-data_criacao")

    return render(
        request,
        "noticias/noticia.html",
        {
            "publicacao": publicacao,
            "comentarios": comentarios_publicados,
            "erro_comentario": erro_comentario,
            "comentario_enviado": request.GET.get("enviado") == "1",
            "leitor_conectado": eh_leitor(request),
        }
    )


# PAINEL DO JORNALISTA
def painel(request):
    if not usuario_logado(request):
        return redirect("login")

    if eh_administrador(request):
        return redirect("administracao")

    publicacoes = Noticia.objects.filter(
        autor_email=request.session.get("usuario_email")
    ).order_by("-data_criacao")

    return render(
        request,
        "noticias/painel.html",
        {
            "publicacoes": publicacoes,
            "total_publicacoes": publicacoes.count(),
            "total_rascunhos": publicacoes.filter(
                status="rascunho"
            ).count(),
            "usuario_tipo": request.session.get("usuario_tipo"),
            "usuario_email": request.session.get("usuario_email"),
        }
    )


# CADASTRAR NOTÍCIA
def nova_noticia(request):
    if not usuario_logado(request):
        return redirect("login")

    regioes = Noticia.REGIAO_CHOICES

    if request.method == "POST":
        status = request.POST.get("status", "rascunho")
        regiao = request.POST.get("regiao", "")

        if status not in ["rascunho", "publicado"]:
            status = "rascunho"

        regioes_validas = [valor for valor, nome in regioes]

        if regiao not in regioes_validas:
            regiao = ""

        Noticia.objects.create(
            titulo=request.POST.get("titulo", "").strip(),
            resumo=request.POST.get("resumo", "").strip(),
            categoria=request.POST.get("categoria", "").strip(),
            local=request.POST.get("local", "").strip(),
            regiao=regiao,
            imagem=request.POST.get("imagem", "").strip(),
            conteudo=request.POST.get("conteudo", "").strip(),
            tags=request.POST.get("tags", "").strip(),
            status=status,
            autor_email=request.session.get("usuario_email", "")
        )

        return redirecionar_painel(request)

    return render(
        request,
        "noticias/nova_noticia.html",
        {"regioes": regioes}
    )


# EDITAR NOTÍCIA — SOMENTE ADMINISTRADOR
def editar_noticia(request, id):
    if not eh_administrador(request):
        return redirecionar_painel(request) if usuario_logado(request) else redirect("login")

    publicacao = get_object_or_404(Noticia, id=id)
    regioes = Noticia.REGIAO_CHOICES

    if request.method == "POST":
        status = request.POST.get("status", "rascunho")
        regiao = request.POST.get("regiao", "")

        if status not in ["rascunho", "publicado"]:
            status = "rascunho"

        regioes_validas = [valor for valor, nome in regioes]

        if regiao not in regioes_validas:
            regiao = ""

        publicacao.titulo = request.POST.get("titulo", "").strip()
        publicacao.resumo = request.POST.get("resumo", "").strip()
        publicacao.categoria = request.POST.get("categoria", "").strip()
        publicacao.local = request.POST.get("local", "").strip()
        publicacao.regiao = regiao
        publicacao.imagem = request.POST.get("imagem", "").strip()
        publicacao.conteudo = request.POST.get("conteudo", "").strip()
        publicacao.tags = request.POST.get("tags", "").strip()
        publicacao.status = status

        publicacao.save()

        return redirect("administracao")

    return render(
        request,
        "noticias/nova_noticia.html",
        {
            "publicacao": publicacao,
            "regioes": regioes,
        }
    )


# EXCLUIR NOTÍCIA — SOMENTE ADMINISTRADOR
@require_POST
def excluir_noticia(request, id):
    if not eh_administrador(request):
        return redirecionar_painel(request) if usuario_logado(request) else redirect("login")

    publicacao = get_object_or_404(Noticia, id=id)
    publicacao.delete()

    return redirect("administracao")


# EXPLORAR NOTÍCIAS — ACESSO PÚBLICO
def explorar(request):
    publicacoes = Noticia.objects.filter(
        status="publicado"
    ).order_by("-data_criacao")

    return render(
        request,
        "noticias/explorar.html",
        {"publicacoes": publicacoes}
    )


# PUBLICAÇÕES — JORNALISTA
def minhas_publicacoes(request):
    if not eh_jornalista(request):
        return redirecionar_painel(request) if usuario_logado(request) else redirect("login")

    publicacoes = Noticia.objects.filter(
        autor_email=request.session.get("usuario_email")
    ).order_by("-data_criacao")

    return render(
        request,
        "noticias/minhas_publicacoes.html",
        {
            "publicacoes": publicacoes,
            "total_publicacoes": publicacoes.count(),
            "total_publicadas": publicacoes.filter(status="publicado").count(),
            "total_rascunhos": publicacoes.filter(status="rascunho").count(),
            "usuario_email": request.session.get("usuario_email"),
        }
    )


# COMENTÁRIOS — SOMENTE ADMINISTRADOR
def comentarios(request):
    if not eh_administrador(request):
        return redirecionar_painel(request) if usuario_logado(request) else redirect("login")

    pendentes = Comentario.objects.filter(
        aprovado=False
    ).order_by("-data_criacao")

    aprovados = Comentario.objects.filter(
        aprovado=True
    ).order_by("-data_criacao")

    return render(
        request,
        "noticias/comentarios.html",
        {
            "pendentes": pendentes,
            "aprovados": aprovados,
            "usuario_email": request.session.get("usuario_email"),
        }
    )


# MODERAR COMENTÁRIOS — SOMENTE ADMINISTRADOR
@require_POST
def moderar_comentario(request, id, acao):
    if not eh_administrador(request):
        return redirecionar_painel(request) if usuario_logado(request) else redirect("login")

    comentario = get_object_or_404(Comentario, id=id)

    if acao == "aprovar":
        comentario.aprovado = True
        comentario.save()

    elif acao == "rejeitar":
        comentario.delete()

    return redirect("comentarios")


# PAINEL DO ADMINISTRADOR
def administracao(request):
    if not eh_administrador(request):
        return redirecionar_painel(request) if usuario_logado(request) else redirect("login")

    publicacoes = Noticia.objects.all().order_by("-data_criacao")

    return render(
        request,
        "noticias/administracao.html",
        {
            "publicacoes": publicacoes,
            "total_publicacoes": publicacoes.count(),
            "total_rascunhos": publicacoes.filter(
                status="rascunho"
            ).count(),
            "total_comentarios": Comentario.objects.count(),
            "total_pendentes": Comentario.objects.filter(
                aprovado=False
            ).count(),
            "usuario_email": request.session.get("usuario_email"),
        }
    )


# CADASTRO DE LEITORES — DEMONSTRAÇÃO
def cadastro_leitor(request):
    return render(
        request,
        "noticias/cadastro_leitor.html"
    )


# PORTAL DO LEITOR
def portal_leitor(request):
    if not eh_leitor(request):
        return redirect("login")

    publicacoes = Noticia.objects.filter(
        status="publicado"
    ).order_by("-data_criacao")

    favoritos_ids = request.session.get("favoritos", [])

    noticias_salvas = Noticia.objects.filter(
        id__in=favoritos_ids,
        status="publicado"
    ).order_by("-data_criacao")

    meus_comentarios = Comentario.objects.filter(
        autor_email=request.session.get("usuario_email")
    ).select_related("noticia").order_by("-data_criacao")

    return render(
        request,
        "noticias/portal_leitor.html",
        {
            "publicacoes": publicacoes,
            "noticias_salvas": noticias_salvas,
            "favoritos_ids": favoritos_ids,
            "usuario_email": request.session.get("usuario_email"),
            "meus_comentarios": meus_comentarios,
        }
    )


# ADICIONAR OU REMOVER FAVORITOS
@require_POST
def alternar_favorito(request, id):
    if not eh_leitor(request):
        return redirect("login")

    get_object_or_404(
        Noticia,
        id=id,
        status="publicado"
    )

    favoritos = request.session.get("favoritos", [])

    if id in favoritos:
        favoritos.remove(id)
    else:
        favoritos.append(id)

    request.session["favoritos"] = favoritos

    return redirect("/leitor/#salvos")
