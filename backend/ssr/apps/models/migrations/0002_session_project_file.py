# Generated by Django 3.1 on 2020-08-27 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='project_file',
            field=models.CharField(max_length=1024, null=True),
        ),
    ]
