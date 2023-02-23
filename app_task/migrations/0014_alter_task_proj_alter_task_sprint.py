# Generated by Django 4.1.5 on 2023-02-23 15:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_task', '0013_task_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='proj',
            field=models.ForeignKey(blank=True, help_text='Проект', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='proj_tasks', to='app_task.proj', verbose_name='Проект'),
        ),
        migrations.AlterField(
            model_name='task',
            name='sprint',
            field=models.ForeignKey(blank=True, help_text='Спринт', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sprint_tasks', to='app_task.sprint', verbose_name='Спринт'),
        ),
    ]
