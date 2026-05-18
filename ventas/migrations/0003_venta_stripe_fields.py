from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0002_alter_venta_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='venta',
            name='stripe_payment_intent',
            field=models.CharField(
                max_length=200,
                blank=True,
                default='',
                verbose_name='Stripe Payment Intent ID',
            ),
        ),
        migrations.AddField(
            model_name='venta',
            name='stripe_status',
            field=models.CharField(
                max_length=50,
                blank=True,
                default='',
                verbose_name='Estado Stripe',
            ),
        ),
    ]
