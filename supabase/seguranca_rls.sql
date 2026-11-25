-- Rode UMA vez no Supabase: SQL Editor > New query > Run
-- (depois de executar "python manage.py migrate")
--
-- O Supabase expõe as tabelas do schema "public" por uma API REST pública.
-- Ativar o RLS (Row Level Security) sem criar políticas bloqueia esse acesso
-- externo. O Django continua funcionando normalmente, pois conecta com o
-- usuário "postgres", que ignora o RLS.

DO $$
DECLARE
    tabela record;
BEGIN
    FOR tabela IN
        SELECT tablename FROM pg_tables WHERE schemaname = 'public'
    LOOP
        EXECUTE format(
            'ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY;',
            tabela.tablename
        );
    END LOOP;
END $$;
