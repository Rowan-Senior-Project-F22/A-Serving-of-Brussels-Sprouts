# Generated by Django 3.2.15 on 2022-11-03 23:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0003_auto_20221102_1615'),
    ]

    operations = [
        migrations.RenameField(
            model_name='messagemodel',
            old_name='reciever_user',
            new_name='receiver_user',
        ),
    ]