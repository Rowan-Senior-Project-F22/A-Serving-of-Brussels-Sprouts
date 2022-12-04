# Generated by Django 3.2.15 on 2022-11-28 01:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0002_auto_20221029_1900'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_name', models.CharField(max_length=25)),
                ('room_slug', models.SlugField(unique=True)),
            ],
        ),
    ]