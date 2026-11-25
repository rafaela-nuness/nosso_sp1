import os
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

# Caminho principal do projeto
BASE_DIR = Path(__file__).resolve().parent.parent


# Lê o arquivo .env (se existir) para preencher as variáveis de ambiente.
# Veja o arquivo .env.example para saber o que configurar.
try:
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass


def env_bool(nome, padrao=False):
    valor = os.environ.get(nome)

    if valor is None:
        return padrao

    return valor.strip().lower() in ("1", "true", "yes", "sim", "on")


def env_lista(nome):
    return [
        item.strip()
        for item in os.environ.get(nome, "").split(",")
        if item.strip()
    ]


# Configurações de segurança
# Em produção, defina SECRET_KEY e DEBUG=False no arquivo .env.
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-!3t#=t0y^m&=o&53&v#lk*%0--ic4uz*%35mn*ke!+jww3ur"
)

DEBUG = env_bool("DEBUG", True)

ALLOWED_HOSTS = env_lista("ALLOWED_HOSTS")

CSRF_TRUSTED_ORIGINS = env_lista("CSRF_TRUSTED_ORIGINS")


# Aplicativos instalados
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'noticias',
]


# Configurações de requisições
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'config.urls'


# Configuração dos templates HTML
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'config.wsgi.application'


# Banco de dados
# Com a variável DATABASE_URL definida no .env, o site usa o PostgreSQL
# do Supabase. Sem ela, continua usando o SQLite local (db.sqlite3).
def banco_de_dados():
    url = os.environ.get("DATABASE_URL", "").strip()

    if not url:
        return {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

    dados = urlparse(url)
    porta = dados.port or 5432
    opcoes = {
        chave: valores[0]
        for chave, valores in parse_qs(dados.query).items()
    }
    opcoes.setdefault("sslmode", "require")

    configuracao = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': unquote(dados.path.lstrip("/")) or "postgres",
        'USER': unquote(dados.username or ""),
        'PASSWORD': unquote(dados.password or ""),
        'HOST': dados.hostname or "",
        'PORT': porta,
        'CONN_MAX_AGE': int(os.environ.get("DB_CONN_MAX_AGE", "60")),
        'OPTIONS': opcoes,
    }

    # O "Transaction pooler" do Supabase (porta 6543) não aceita cursores
    # do lado do servidor nem conexões persistentes.
    if porta == 6543:
        configuracao['DISABLE_SERVER_SIDE_CURSORS'] = True
        configuracao['CONN_MAX_AGE'] = 0

    return {'default': configuracao}


DATABASES = banco_de_dados()


# Validação de senhas
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Idioma e fuso horário
LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Arquivos estáticos: CSS, JavaScript e imagens
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]


# Tipo padrão de chave primária
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Chave da API do Geoapify (mapa da página da notícia).
# Defina GEOAPIFY_API_KEY no arquivo .env.
GEOAPIFY_API_KEY = os.environ.get(
    "GEOAPIFY_API_KEY",
    "f73beb4cb8c849f0a2ca9139a6728752"
)
