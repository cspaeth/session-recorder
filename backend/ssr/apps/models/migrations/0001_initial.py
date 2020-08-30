# Generated by Django 3.1 on 2020-08-27 13:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('username', models.CharField(max_length=30)),
                ('next_take_number', models.IntegerField(default=1)),
                ('next_take_name', models.CharField(default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Take',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('location', models.FloatField()),
                ('length', models.FloatField(null=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='takes', to='models.session')),
            ],
        ),
    ]