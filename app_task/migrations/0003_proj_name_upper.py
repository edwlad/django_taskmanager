# Generated by Django 4.1.5 on 2023-03-11 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_task', '0002_taskstep_auto_create'),
    ]

    operations = [
        migrations.AddField(
            model_name='proj',
            name='name_upper',
            field=models.CharField(blank=True, help_text='Название проекта в верхнем регистре', max_length=120, verbose_name='НАЗВАНИЕ'),
        ),
    ]