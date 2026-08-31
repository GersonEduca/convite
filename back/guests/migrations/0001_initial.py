from django.db import migrations, models


def create_initial_guests(apps, schema_editor):
    Guest = apps.get_model('guests', 'Guest')
    Guest.objects.bulk_create([
        Guest(name=f'Nome {number}') for number in range(1, 9)
    ])


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Guest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('response', models.CharField(
                    choices=[
                        ('pending', 'Pendente'),
                        ('confirmed', 'Confirmado'),
                        ('declined', 'Negado'),
                    ],
                    default='pending',
                    max_length=20,
                )),
            ],
        ),
        migrations.RunPython(create_initial_guests, migrations.RunPython.noop),
    ]