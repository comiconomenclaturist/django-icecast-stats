# Generated by Django 2.2.2 on 2019-07-09 14:59

import django.contrib.postgres.fields.ranges
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('useragent', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IngestParameters',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minimum_duration', models.PositiveSmallIntegerField(default=3, help_text='Minimum listener duration (in seconds) required to import connection to database', validators=[django.core.validators.MinValueValidator(1)])),
                ('session_threshold', models.PositiveSmallIntegerField(default=120, help_text='Maximum gap between connections (in seconds) to concatenate connections to sessions')),
            ],
            options={
                'verbose_name': 'Ingest Parameters',
                'verbose_name_plural': 'Ingest Parameters',
            },
        ),
        migrations.CreateModel(
            name='Stream',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mountpoint', models.CharField(max_length=255, unique=True)),
                ('bitrate', models.PositiveSmallIntegerField()),
            ],
            options={
                'ordering': ('-bitrate', 'mountpoint'),
            },
        ),
        migrations.CreateModel(
            name='Listener',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(verbose_name='IP address')),
                ('session', django.contrib.postgres.fields.ranges.DateTimeRangeField()),
                ('duration', models.DurationField()),
                ('referer', models.CharField(max_length=255)),
                ('country', django_countries.fields.CountryField(max_length=2, null=True)),
                ('city', models.CharField(max_length=255, null=True)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9, null=True)),
                ('stream', models.ForeignKey(on_delete='PROTECT', to='listener.Stream')),
                ('user_agent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='useragent.UserAgent')),
            ],
            options={
                'ordering': ('session',),
                'unique_together': {('ip_address', 'stream', 'session', 'user_agent')},
            },
        ),
    ]