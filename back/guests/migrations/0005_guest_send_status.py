from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guests', '0004_guest_side_family'),
    ]

    operations = [
        migrations.AddField(
            model_name='guest',
            name='send_status',
            field=models.CharField(
                choices=[('to_send', 'Enviar'), ('sent', 'Enviado'), ('resend', 'Reenviar')],
                default='to_send',
                max_length=10,
                verbose_name='Status de envio',
            ),
        ),
    ]