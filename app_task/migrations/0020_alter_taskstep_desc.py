# Generated by Django 4.1.5 on 2023-03-03 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_task', '0019_alter_proj_uweb_alter_sprint_uweb_alter_task_parent_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskstep',
            name='desc',
            field=models.TextField(help_text='Выполненная работа по задаче', verbose_name='Что сделано'),
        ),
    ]
