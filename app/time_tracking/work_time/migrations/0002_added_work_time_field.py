# Generated by Django 3.0.9 on 2020-08-07 06:44

from django.db import migrations, models


def calculate_finished_work_times(apps, schema_editor):
    WorkTimes = apps.get_model('work_time', 'WorkTime')
    for work_time in WorkTimes.objects.all().iterator():
        if work_time.start_time is not None and work_time.end_time is not None:
            work_time.work_time = int((work_time.end_time - work_time.start_time).total_seconds())
            work_time.save()

def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('work_time', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='worktime',
            name='work_time',
            field=models.PositiveIntegerField(blank=True, editable=False, null=True),
        ),
        migrations.RunPython(calculate_finished_work_times, reverse_func),

    ]
