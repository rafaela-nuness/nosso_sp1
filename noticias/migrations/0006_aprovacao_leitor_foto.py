from django.db import migrations, models


def aprovar_comentarios_existentes(apps, schema_editor):
    Comentario = apps.get_model("noticias", "Comentario")
    Comentario.objects.filter(aprovado=False).update(aprovado=True)


def nada(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("noticias", "0005_comentario_autor_email"),
    ]

    operations = [
        migrations.AddField(
            model_name="noticia",
            name="foto",
            field=models.FileField(blank=True, upload_to="noticias/"),
        ),
        migrations.AlterField(
            model_name="noticia",
            name="status",
            field=models.CharField(
                choices=[
                    ("rascunho", "Rascunho"),
                    ("pendente", "Aguardando aprovação"),
                    ("publicado", "Aceita"),
                    ("negado", "Negada"),
                ],
                default="rascunho",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="comentario",
            name="aprovado",
            field=models.BooleanField(default=True),
        ),
        migrations.RunPython(aprovar_comentarios_existentes, nada),
        migrations.CreateModel(
            name="Leitor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("senha", models.CharField(max_length=128)),
                ("data_criacao", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
