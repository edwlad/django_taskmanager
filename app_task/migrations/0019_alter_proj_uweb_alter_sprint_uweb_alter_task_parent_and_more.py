# Generated by Django 4.1.5 on 2023-02-26 09:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app_task', '0018_alter_taskstep_date_end'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proj',
            name='uweb',
            field=models.ForeignKey(blank=True, help_text='Последний прользователь редактировавший проект', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Редактор'),
        ),
        migrations.AlterField(
            model_name='sprint',
            name='uweb',
            field=models.ForeignKey(blank=True, help_text='Последний прользователь редактировавший спринт', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Редактор'),
        ),
        migrations.AlterField(
            model_name='task',
            name='parent',
            field=models.ForeignKey(blank=True, help_text='Предыдущая задача', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='parent_nexts', to='app_task.task', verbose_name='Зависит от'),
        ),
        migrations.AlterField(
            model_name='task',
            name='proj',
            field=models.ForeignKey(default=1, help_text='Проект', on_delete=django.db.models.deletion.CASCADE, related_name='proj_tasks', to='app_task.proj', verbose_name='Проект'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='task',
            name='uweb',
            field=models.ForeignKey(blank=True, help_text='Последний прользователь редактировавший задачу', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Редактор'),
        ),
    ]
