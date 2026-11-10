from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("noticias", "0006_aprovacao_leitor_foto"),
    ]

    operations = [
        migrations.AddField(
            model_name="leitor",
            name="jornalista",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="SolicitacaoJornalista",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("capacidades", models.TextField()),
                ("experiencia", models.TextField(blank=True)),
                ("curriculo", models.FileField(upload_to="curriculos/")),
                ("status", models.CharField(
                    choices=[
                        ("pendente", "Aguardando análise"),
                        ("entrevista", "Entrevista marcada"),
                        ("aceita", "Aceita"),
                        ("recusada", "Recusada"),
                    ],
                    default="pendente",
                    max_length=20,
                )),
                ("data_entrevista", models.DateTimeField(blank=True, null=True)),
                ("detalhes_entrevista", models.CharField(blank=True, max_length=250)),
                ("data_criacao", models.DateTimeField(auto_now_add=True)),
                ("leitor", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="solicitacoes", to="noticias.leitor")),
            ],
        ),
    ]
