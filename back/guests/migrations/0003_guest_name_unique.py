from django.db import migrations, models
from django.db.models import Count


def merge_duplicate_names(apps, schema_editor):
    guest_model = apps.get_model('guests', 'Guest')
    database = schema_editor.connection.alias
    duplicates = (
        guest_model.objects.using(database)
        .values('name')
        .annotate(total=Count('pk'))
        .filter(total__gt=1)
    )
    duplicate_to_canonical = {}

    for duplicate_group in duplicates.iterator():
        guests = list(
            guest_model.objects.using(database)
            .filter(name=duplicate_group['name'])
            .order_by('pk')
        )
        canonical = guests[0]
        for duplicate in guests[1:]:
            duplicate_to_canonical[duplicate.pk] = canonical.pk
            if not canonical.phone and duplicate.phone:
                canonical.phone = duplicate.phone
            if not canonical.notes and duplicate.notes:
                canonical.notes = duplicate.notes
            if canonical.response == 'pending' and duplicate.response != 'pending':
                canonical.response = duplicate.response
            if canonical.family_head_id is None:
                canonical.family_head_id = duplicate.family_head_id
        canonical.save(update_fields=['phone', 'notes', 'response', 'family_head'])

    for guest in guest_model.objects.using(database).all().iterator():
        family_head_id = duplicate_to_canonical.get(guest.family_head_id, guest.family_head_id)
        if family_head_id == guest.pk:
            family_head_id = None
        if family_head_id != guest.family_head_id:
            guest_model.objects.using(database).filter(pk=guest.pk).update(family_head_id=family_head_id)

    guest_model.objects.using(database).filter(pk__in=duplicate_to_canonical).delete()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('guests', '0002_guest_family_head_guest_notes_guest_phone_guest_slug_and_more'),
    ]

    operations = [
        migrations.RunPython(merge_duplicate_names, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='guest',
            name='name',
            field=models.CharField(max_length=120, unique=True, verbose_name='Nome'),
        ),
    ]