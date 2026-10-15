import uuid

from django.db import migrations, models

import guests.models


class Migration(migrations.Migration):

    dependencies = [
        ('guests', '0006_guest_send_status_resent'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeddingPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(upload_to=guests.models.wedding_photo_upload_path, verbose_name='Imagem')),
                ('delete_token', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Enviada em')),
            ],
            options={
                'ordering': ['-created_at', '-id'],
            },
        ),
    ]
