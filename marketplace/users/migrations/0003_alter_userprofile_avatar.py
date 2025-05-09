# Generated by Django 5.1.4 on 2025-04-20 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_customuser_options_customuser_username_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(blank=True, default='images/default-avatar.png', null=True, upload_to='users/avatars/'),
        ),
    ]
