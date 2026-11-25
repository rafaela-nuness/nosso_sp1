# Nosso SP

Portal de notícias dos bairros de São Paulo (Django).

## Rodar no seu computador

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env        # Linux/Mac: cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Sem `DATABASE_URL` no `.env`, o site usa o SQLite local (`db.sqlite3`).

## Conectar ao banco online (Supabase)

1. Crie um projeto em https://supabase.com.
2. No projeto: **Project Settings > Database > Connection string > URI**.
   Copie a string e troque `[YOUR-PASSWORD]` pela senha do banco.
   - Porta `5432` (Session pooler) é a mais simples para o dia a dia.
   - Porta `6543` (Transaction pooler) também é aceita; o `settings.py` já se ajusta.
3. Cole a string no `.env`, na linha `DATABASE_URL=`.
4. Crie as tabelas no Supabase: `python manage.py migrate`
5. (Opcional) Crie o superusuário do `/admin/`: `python manage.py createsuperuser`
6. No Supabase, abra **SQL Editor** e rode o arquivo `supabase/seguranca_rls.sql`
   (bloqueia o acesso público às tabelas pela API do Supabase; o Django não é afetado).

### Levar os dados que já estão no SQLite para o Supabase

Faça isto **antes** de colocar a `DATABASE_URL` no `.env` (ainda usando o SQLite):

```bash
python manage.py dumpdata noticias --natural-foreign --indent 2 -o dados.json
```

Depois coloque a `DATABASE_URL`, rode `python manage.py migrate` e então:

```bash
python manage.py loaddata dados.json
```

> As fotos e certificados enviados ficam na pasta `media/` do servidor
> (o Supabase guarda apenas o caminho do arquivo no banco).

## Estrutura do banco

Veja `DATABASE.md` (tabelas e relacionamentos).
