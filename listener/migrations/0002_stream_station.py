# Generated by Django 2.2.2 on 2019-07-29 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listener', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stream',
            name='station',
            field=models.CharField(choices=[('R', 'Resonance'), ('E', 'Extra')], default='R', max_length=1),
            preserve_default=False,
        ),
    ]