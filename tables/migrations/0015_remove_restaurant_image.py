# Generated by Django 3.0.4 on 2020-04-17 22:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0014_auto_20200417_1503'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restaurant',
            name='image',
        ),
    ]