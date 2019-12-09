# Generated by Django 2.2.2 on 2019-08-01 15:01

import django.contrib.postgres.fields.ranges
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listener', '0002_stream_station'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stream',
            options={'ordering': ('-station', '-bitrate', 'mountpoint')},
        ),
        migrations.CreateModel(
            name='ListenerAggregate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', django.contrib.postgres.fields.ranges.DateTimeRangeField()),
                ('count', models.PositiveIntegerField()),
                ('duration', models.DurationField()),
                ('stream', models.ForeignKey(on_delete=models.PROTECT, to='listener.Stream')),
            ],
            options={
                'ordering': ['period'],
            },
        ),
    ]
