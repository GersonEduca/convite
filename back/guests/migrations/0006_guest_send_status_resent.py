from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guests', '0005_guest_send_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guest',
            name='send_status',
            field=models.CharField(
                choices=[
                    ('to_send', 'Enviar'),
                    ('sent', 'Enviado'),
                    ('resend', 'Reenviar'),
                    ('resent', 'Reenviado'),
                ],
                default='to_send',
                max_length=10,
                verbose_name='Status de envio',
            ),
        ),
    ]