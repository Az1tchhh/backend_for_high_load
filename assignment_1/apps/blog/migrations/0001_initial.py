# Generated by Django 5.1.1 on 2024-09-07 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('author', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
