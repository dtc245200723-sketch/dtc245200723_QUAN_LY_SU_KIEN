from django.db import migrations, models


def assign_event_codes(apps, schema_editor):
    Event = apps.get_model('events', 'Event')
    for event in Event.objects.order_by('id').iterator():
        event.event_code = f'EVT{event.pk:06d}'
        event.save(update_fields=['event_code'])


class Migration(migrations.Migration):
    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='event_code',
            field=models.CharField(blank=True, default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='registration_deadline',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='category',
            field=models.CharField(default='Sự kiện', max_length=80),
        ),
        migrations.AddField(
            model_name='registration',
            name='attendee_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='registration',
            name='phone',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.RunPython(assign_event_codes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='event',
            name='event_code',
            field=models.CharField(blank=True, max_length=20, unique=True),
        ),
    ]
