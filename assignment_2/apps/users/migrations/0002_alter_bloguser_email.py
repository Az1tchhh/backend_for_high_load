# Generated by Django 5.1.1 on 2024-10-06 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bloguser',
            name='email',
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
    ]
