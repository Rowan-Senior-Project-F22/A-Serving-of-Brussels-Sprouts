# Generated by Django 3.2.15 on 2022-12-14 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0009_auto_20221213_1340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='preferences',
            field=models.CharField(default='{"likes": [], "dislikes": [], "friends": "Default"}', max_length=1000),
        ),
    ]