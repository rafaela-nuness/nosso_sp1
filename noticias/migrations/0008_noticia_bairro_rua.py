from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("noticias", "0007_solicitacao_jornalista"),
    ]

    operations = [
        migrations.AddField(
            model_name="noticia",
            name="bairro",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="noticia",
            name="rua",
            field=models.CharField(blank=True, default="", max_length=150),
        ),
    ]
