# Generated by Django 3.0.4 on 2020-04-17 21:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0012_auto_20200417_1458'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='image',
        ),
    ]