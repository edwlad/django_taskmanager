# Generated by Django 4.1.5 on 2023-02-08 13:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_task', '0003_sprint_proj_alter_proj_author_alter_sprint_author_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='proj',
            field=models.ForeignKey(blank=True, help_text='Проект', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='proj_tasks', to='app_task.proj', verbose_name='Проект'),
        ),
    ]
