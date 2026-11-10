from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("noticias", "0008_noticia_bairro_rua"),
    ]

    operations = [
        migrations.AddField(
            model_name="solicitacaojornalista",
            name="nome_completo",
            field=models.CharField(blank=True, default="", max_length=150),
        ),
        migrations.AddField(
            model_name="solicitacaojornalista",
            name="cpf",
            field=models.CharField(blank=True, default="", max_length=14),
        ),
        migrations.AddField(
            model_name="solicitacaojornalista",
            name="zona",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AddField(
            model_name="solicitacaojornalista",
            name="bairro",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AlterField(
            model_name="solicitacaojornalista",
            name="curriculo",
            field=models.FileField(blank=True, upload_to="curriculos/"),
        ),
        migrations.CreateModel(
            name="CertificadoSolicitacao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("imagem", models.FileField(upload_to="certificados/")),
                ("solicitacao", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="certificados", to="noticias.solicitacaojornalista")),
            ],
        ),
    ]
