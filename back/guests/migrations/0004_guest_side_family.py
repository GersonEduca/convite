from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guests', '0003_guest_name_unique'),
    ]

    operations = [
        migrations.AddField(
            model_name='guest',
            name='side_family',
            field=models.CharField(
                blank=True,
                choices=[('noivo', 'Noivo'), ('noiva', 'Noiva')],
                default='',
                max_length=5,
                verbose_name='Lado da família',
            ),
        ),
    ]