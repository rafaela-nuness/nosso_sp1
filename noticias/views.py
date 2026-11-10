
import os

from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .models import (
    Noticia, Comentario, Leitor, SolicitacaoJornalista,
    CertificadoSolicitacao
)

EXTENSOES_FOTO = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
TAMANHO_MAXIMO_FOTO = 5 * 1024 * 1024  # 5 MB
EXTENSOES_CURRICULO = {".pdf", ".doc", ".docx"}
TAMANHO_MAXIMO_CURRICULO = 5 * 1024 * 1024  # 5 MB


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
            request.session["usuario_nome"] = "João Silva"
            return redirect("painel")

        elif email == EMAIL_ADMIN and senha == SENHA_ADMIN:
            request.session["usuario_tipo"] = "administrador"
            request.session["usuario_email"] = email
            request.session["usuario_nome"] = "Administrador"
            return redirect("administracao")

        elif email == EMAIL_LEITOR and senha == SENHA_LEITOR:
            request.session["usuario_tipo"] = "leitor"
            request.session["usuario_email"] = email
            request.session["usuario_nome"] = "Leitor"
            return redirect("portal_leitor")

        leitor = Leitor.objects.filter(email__iexact=email).first()

        if leitor and check_password(senha, leitor.senha):
            iniciar_sessao_leitor(request, leitor)

            if leitor.jornalista:
                return redirect("painel")

            return redirect("portal_leitor")

        erro = "E-mail ou senha incorretos."

    return render(
        request,
        "noticias/login.html",
        {"erro": erro}
    )


def iniciar_sessao_leitor(request, leitor):
    request.session.flush()
    request.session["usuario_tipo"] = (
        "jornalista" if leitor.jornalista else "leitor"
    )
    request.session["usuario_email"] = leitor.email
    request.session["usuario_nome"] = leitor.nome


# LOGOUT
def logout(request):
    request.session.flush()
    return redirect("login")


# DETALHES DA NOTÍCIA E COMENTÁRIOS
def noticia(request):
    publicacao_id = request.GET.get("id")

    if eh_administrador(request):
        # O administrador pode ler qualquer notícia para decidir se aprova.
        publicacao = get_object_or_404(Noticia, id=publicacao_id)
    else:
        publicacao = get_object_or_404(
            Noticia,
            id=publicacao_id,
            status="publicado"
        )

    erro_comentario = ""

    if request.method == "POST":
        texto = request.POST.get("comentario", "").strip()
        nome = request.session.get("usuario_nome", "").strip()

        if not usuario_logado(request) and not eh_leitor(request):
            erro_comentario = "Entre na sua conta para comentar."

        elif not texto:
            erro_comentario = "Escreva seu comentário."

        else:
            # O nome vem sempre da conta; o leitor não digita nome.
            Comentario.objects.create(
                noticia=publicacao,
                nome=nome[:100] or "Leitor",
                autor_email=request.session.get("usuario_email", ""),
                texto=texto,
                aprovado=True
            )

            return redirect(
                f"/noticia/?id={publicacao.id}&enviado=1"
            )

    comentarios_publicados = Comentario.objects.filter(
        noticia=publicacao,
        aprovado=True
    ).order_by("-data_criacao")

    favoritos_ids = request.session.get("favoritos", [])

    return render(
        request,
        "noticias/noticia.html",
        {
            "publicacao": publicacao,
            "comentarios": comentarios_publicados,
            "erro_comentario": erro_comentario,
            "comentario_enviado": request.GET.get("enviado") == "1",
            "google_maps_key": (
                settings.GOOGLE_MAPS_API_KEY
                if settings.GOOGLE_MAPS_API_KEY != "COLE_SUA_CHAVE_AQUI"
                else ""
            ),
            "leitor_conectado": eh_leitor(request),
            "pode_comentar": request.session.get("usuario_tipo") in [
                "leitor", "jornalista", "administrador"
            ],
            "favorita": publicacao.id in favoritos_ids,
            "nome_leitor": request.session.get("usuario_nome", ""),
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
            "total_aguardando": publicacoes.filter(
                status="pendente"
            ).count(),
            "total_aceitas": publicacoes.filter(
                status="publicado"
            ).count(),
            "usuario_tipo": request.session.get("usuario_tipo"),
            "usuario_email": request.session.get("usuario_email"),
        }
    )


def validar_foto(arquivo):
    """Retorna uma mensagem de erro, ou "" se a foto for válida."""
    extensao = os.path.splitext(arquivo.name)[1].lower()

    if extensao not in EXTENSOES_FOTO:
        return "Envie uma imagem nos formatos JPG, PNG, WEBP ou GIF."

    if arquivo.size > TAMANHO_MAXIMO_FOTO:
        return "A imagem deve ter no máximo 5 MB."

    return ""


# CADASTRAR NOTÍCIA — SOMENTE JORNALISTA
def nova_noticia(request):
    return formulario_noticia(request, None)


# ABRIR E EDITAR RASCUNHO — SOMENTE O JORNALISTA AUTOR
def editar_noticia(request, id):
    if not eh_jornalista(request):
        return redirecionar_painel(request) if usuario_logado(request) else redirect("login")

    publicacao = get_object_or_404(
        Noticia,
        id=id,
        autor_email=request.session.get("usuario_email", ""),
        status="rascunho"
    )

    return formulario_noticia(request, publicacao)


def formulario_noticia(request, instancia):
    if not eh_jornalista(request):
        return redirecionar_painel(request) if usuario_logado(request) else redirect("login")

    regioes = Noticia.REGIAO_CHOICES
    erro = ""

    if request.method == "POST":
        status = request.POST.get("status", "rascunho")
        regiao = request.POST.get("regiao", "")

        # O jornalista salva rascunho ou envia para aprovação;
        # quem publica de fato é o administrador.
        if status not in ["rascunho", "pendente"]:
            status = "pendente" if status == "publicado" else "rascunho"

        regioes_validas = [valor for valor, nome in regioes]

        if regiao not in regioes_validas:
            regiao = ""

        foto = request.FILES.get("foto")

        if foto:
            erro = validar_foto(foto)

        if not erro:
            noticia_salva = instancia or Noticia(
                autor_email=request.session.get("usuario_email", "")
            )

            bairro = request.POST.get("bairro", "").strip()
            rua = request.POST.get("rua", "").strip()

            noticia_salva.titulo = request.POST.get("titulo", "").strip()
            noticia_salva.resumo = request.POST.get("resumo", "").strip()
            noticia_salva.categoria = request.POST.get("categoria", "").strip()
            noticia_salva.bairro = bairro
            noticia_salva.rua = rua
            # "local" resume o endereço nos cards (início, explorar).
            noticia_salva.local = ", ".join(
                parte for parte in [rua, bairro] if parte
            )[:150]
            noticia_salva.regiao = regiao
            noticia_salva.imagem = request.POST.get("imagem", "").strip()
            noticia_salva.conteudo = request.POST.get("conteudo", "").strip()
            noticia_salva.tags = request.POST.get("tags", "").strip()
            noticia_salva.status = status

            if foto:
                noticia_salva.foto = foto

            noticia_salva.save()

            return redirect("painel")

    return render(
        request,
        "noticias/nova_noticia.html",
        {
            "regioes": regioes,
            "erro": erro,
            "dados": request.POST if request.method == "POST" else instancia,
            "editando": instancia,
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


# APROVAR OU NEGAR NOTÍCIA — SOMENTE ADMINISTRADOR
@require_POST
def moderar_noticia(request, id, acao):
    if not eh_administrador(request):
        return redirecionar_painel(request) if usuario_logado(request) else redirect("login")

    publicacao = get_object_or_404(Noticia, id=id)

    if acao == "aprovar":
        publicacao.status = "publicado"
        publicacao.save()

    elif acao == "negar":
        publicacao.status = "negado"
        publicacao.save()

    return redirect("/administracao/#aprovar")


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
            "total_aguardando": publicacoes.filter(status="pendente").count(),
            "total_rascunhos": publicacoes.filter(status="rascunho").count(),
            "usuario_email": request.session.get("usuario_email"),
        }
    )


# PAINEL DO ADMINISTRADOR
def administracao(request):
    if not eh_administrador(request):
        return redirecionar_painel(request) if usuario_logado(request) else redirect("login")

    publicacoes = Noticia.objects.exclude(
        status="rascunho"
    ).order_by("-data_criacao")

    pendentes = publicacoes.filter(status="pendente")

    solicitacoes = SolicitacaoJornalista.objects.select_related(
        "leitor"
    ).prefetch_related("certificados").order_by("-data_criacao")

    solicitacoes_abertas = solicitacoes.filter(
        status__in=["pendente", "entrevista"]
    )

    return render(
        request,
        "noticias/administracao.html",
        {
            "publicacoes": publicacoes,
            "pendentes": pendentes,
            "solicitacoes": solicitacoes,
            "total_solicitacoes": solicitacoes_abertas.count(),
            "total_aceitas": publicacoes.filter(status="publicado").count(),
            "total_negadas": publicacoes.filter(status="negado").count(),
            "total_pendentes": pendentes.count(),
            "usuario_email": request.session.get("usuario_email"),
        }
    )


# CADASTRO DE LEITORES
def cadastro_leitor(request):
    erro = ""
    dados = {}

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip().lower()
        senha = request.POST.get("senha", "")
        confirmar = request.POST.get("confirmar", "")

        dados = {"nome": nome, "email": email}

        emails_reservados = [
            EMAIL_JORNALISTA.lower(),
            EMAIL_ADMIN.lower(),
            EMAIL_LEITOR.lower(),
        ]

        if not nome or not email or not senha:
            erro = "Preencha todos os campos."

        elif len(nome) > 100:
            erro = "O nome deve ter no máximo 100 caracteres."

        elif len(senha) < 6:
            erro = "A senha deve ter pelo menos 6 caracteres."

        elif senha != confirmar:
            erro = "As senhas não coincidem."

        elif (
            email in emails_reservados
            or Leitor.objects.filter(email__iexact=email).exists()
        ):
            erro = "Já existe uma conta com este e-mail."

        else:
            leitor = Leitor.objects.create(
                nome=nome,
                email=email,
                senha=make_password(senha)
            )

            iniciar_sessao_leitor(request, leitor)

            # Após cadastrar, o leitor vai para a página inicial
            # já com o perfil e o acesso ao dashboard.
            return redirect("home")

    return render(
        request,
        "noticias/cadastro_leitor.html",
        {"erro": erro, "dados": dados}
    )


# PORTAL DO LEITOR
def portal_leitor(request):
    if not eh_leitor(request):
        return redirect("login")

    leitor = Leitor.objects.filter(
        email__iexact=request.session.get("usuario_email", "")
    ).first()

    # Se o administrador já aceitou o pedido, o perfil vira jornalista.
    if leitor and leitor.jornalista:
        request.session["usuario_tipo"] = "jornalista"
        return redirect("painel")

    solicitacao = None

    if leitor:
        solicitacao = leitor.solicitacoes.order_by("-data_criacao").first()

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
            "noticias_salvas": noticias_salvas,
            "favoritos_ids": favoritos_ids,
            "usuario_email": request.session.get("usuario_email"),
            "usuario_nome": request.session.get("usuario_nome", "Leitor"),
            "meus_comentarios": meus_comentarios,
            "conta_cadastrada": leitor is not None,
            "solicitacao": solicitacao,
            "erro_solicitacao": request.GET.get("erro_solicitacao", ""),
            "solicitacao_enviada": request.GET.get("solicitacao") == "1",
            "regioes": Noticia.REGIAO_CHOICES,
        }
    )


# PEDIDO PARA VIRAR JORNALISTA — SOMENTE LEITOR
@require_POST
def solicitar_jornalista(request):
    if not eh_leitor(request):
        return redirect("login")

    leitor = Leitor.objects.filter(
        email__iexact=request.session.get("usuario_email", "")
    ).first()

    def voltar_com_erro(mensagem):
        from urllib.parse import quote
        return redirect(
            f"/leitor/?erro_solicitacao={quote(mensagem)}#jornalista"
        )

    if not leitor:
        return voltar_com_erro(
            "Crie uma conta de leitor para enviar sua solicitação."
        )

    if leitor.solicitacoes.filter(
        status__in=["pendente", "entrevista"]
    ).exists():
        return voltar_com_erro("Você já tem uma solicitação em andamento.")

    nome_completo = request.POST.get("nome_completo", "").strip()
    cpf = request.POST.get("cpf", "").strip()
    zona = request.POST.get("zona", "").strip()
    bairro = request.POST.get("bairro", "").strip()
    habilidades = request.POST.get("capacidades", "").strip()
    certificados = request.FILES.getlist("certificados")

    if not nome_completo:
        return voltar_com_erro("Informe seu nome completo.")

    if not cpf_valido(cpf):
        return voltar_com_erro("Informe um CPF válido.")

    if zona not in [valor for valor, nome in Noticia.REGIAO_CHOICES]:
        return voltar_com_erro("Escolha a zona onde você mora.")

    if not bairro:
        return voltar_com_erro("Informe o bairro onde você mora.")

    if not habilidades:
        return voltar_com_erro("Descreva suas habilidades.")

    if not certificados:
        return voltar_com_erro("Anexe pelo menos uma foto de certificado.")

    if len(certificados) > 10:
        return voltar_com_erro("Envie no máximo 10 certificados.")

    for arquivo in certificados:
        erro_foto = validar_foto(arquivo)

        if erro_foto:
            return voltar_com_erro(f"Certificado inválido: {erro_foto}")

    digitos = "".join(c for c in cpf if c.isdigit())
    cpf_formatado = f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"

    solicitacao = SolicitacaoJornalista.objects.create(
        leitor=leitor,
        nome_completo=nome_completo[:150],
        cpf=cpf_formatado,
        zona=zona,
        bairro=bairro[:100],
        capacidades=habilidades
    )

    for arquivo in certificados:
        CertificadoSolicitacao.objects.create(
            solicitacao=solicitacao,
            imagem=arquivo
        )

    return redirect("/leitor/?solicitacao=1#jornalista")


def cpf_valido(cpf):
    digitos = [int(c) for c in cpf if c.isdigit()]

    if len(digitos) != 11 or len(set(digitos)) == 1:
        return False

    for tamanho in (9, 10):
        soma = sum(
            digitos[i] * (tamanho + 1 - i) for i in range(tamanho)
        )
        digito = (soma * 10) % 11 % 10

        if digito != digitos[tamanho]:
            return False

    return True


# DECIDIR SOLICITAÇÃO DE JORNALISTA — SOMENTE ADMINISTRADOR
@require_POST
def decidir_solicitacao(request, id, acao):
    if not eh_administrador(request):
        return redirecionar_painel(request) if usuario_logado(request) else redirect("login")

    solicitacao = get_object_or_404(SolicitacaoJornalista, id=id)

    if solicitacao.status in ["aceita", "recusada"]:
        return redirect("/administracao/#solicitacoes")

    if acao == "entrevista":
        data = parse_datetime(request.POST.get("data_entrevista", ""))

        if data:
            if timezone.is_naive(data):
                data = timezone.make_aware(data)

            solicitacao.data_entrevista = data
            solicitacao.detalhes_entrevista = request.POST.get(
                "detalhes_entrevista", ""
            ).strip()[:250]
            solicitacao.status = "entrevista"
            solicitacao.save()

    elif acao in ["liberar", "aceitar"] and solicitacao.status in [
        "pendente", "entrevista"
    ]:
        solicitacao.status = "aceita"
        solicitacao.save()

        # O perfil vira jornalista automaticamente.
        solicitacao.leitor.jornalista = True
        solicitacao.leitor.save()

    elif acao == "recusar":
        solicitacao.status = "recusada"
        solicitacao.save()

    return redirect("/administracao/#solicitacoes")


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

    destino = request.POST.get("next", "")

    if destino and url_has_allowed_host_and_scheme(
        destino,
        allowed_hosts={request.get_host()}
    ):
        return redirect(destino)

    return redirect("/leitor/#salvos")
