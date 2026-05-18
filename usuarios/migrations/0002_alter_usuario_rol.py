# Generated manually for Entrega 2 role update.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='rol',
            field=models.CharField(choices=[('cliente', 'Cliente'), ('propietario', 'Propietario'), ('admin', 'Administrador')], max_length=20),
        ),
    ]
