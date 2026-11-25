# Banco de dados — Nosso SP

## Relacionamentos

| Tabela origem | Coluna | Tipo | Tabela destino | Coluna | Cardinalidade | Ao excluir |
|---|---|---|---|---|---|---|
| noticias_solicitacaojornalista | leitor_id | FK real | noticias_leitor | id | N:1 (um leitor, várias solicitações) | CASCADE |
| noticias_certificadosolicitacao | solicitacao_id | FK real | noticias_solicitacaojornalista | id | N:1 (uma solicitação, vários certificados) | CASCADE |
| noticias_comentario | noticia_id | FK real | noticias_noticia | id | N:1 (uma notícia, vários comentários) | CASCADE |
| noticias_noticia | autor_email | lógico (sem FK) | noticias_leitor | email | N:1 (jornalista autor) | — |
| noticias_comentario | autor_email | lógico (sem FK) | noticias_leitor | email | N:1 (autor do comentário) | — |

Observações:
- Os favoritos do leitor ficam na sessão (`django_session`), não em tabela própria.
- As contas de teste (jornalista, administrador e leitor) estão no código e não existem no banco.
- Tabelas do Django (`auth_*`, `django_session`, `django_migrations`, `django_admin_log`, `django_content_type`) são criadas pelo `migrate`.
