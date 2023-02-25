# Generated by Django 4.1.5 on 2023-02-25 17:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app_task', '0016_task_uweb'),
    ]

    operations = [
        migrations.AddField(
            model_name='proj',
            name='uweb',
            field=models.ForeignKey(blank=True, help_text='Последний прользовател редактировавший проект', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Редактор'),
        ),
        migrations.AddField(
            model_name='sprint',
            name='uweb',
            field=models.ForeignKey(blank=True, help_text='Последний прользовател редактировавший спринт', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Редактор'),
        ),
    ]