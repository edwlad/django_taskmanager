from django.db.models.signals import post_save, post_delete
from app_task.models import Proj, Sprint, Task
from django.core.mail import send_mass_mail
from django.conf import settings  # noqa


def send_email_message(sender, **kwargs):
    obj = kwargs.get("instance", None)
    created = kwargs.get("created", None)

    text = ""
    if created is None:
        text += "Удаление"
    elif created:
        text += "Создание"
    else:
        text += "Обновление"

    users = {}
    if obj.author:
        users.update({obj.author.id: obj.author})
    if sender is Proj:
        users.update(
            {
                v.author.id: v.author
                for v in obj.proj_sprints.exclude(author=None).filter(date_end=None)
            }
        )
        for v in obj.proj_tasks.filter(date_end=None):
            if v.author:
                users.update({v.author.id: v.author})
            if v.user:
                users.update({v.user.id: v.user})
    elif sender is Sprint:
        for v in obj.sprint_tasks.filter(date_end=None):
            if v.author:
                users.update({v.author.id: v.author})
            if v.user:
                users.update({v.user.id: v.user})
    elif sender is Task and obj.user:
        users.update({obj.user.id: obj.user})

    # (subject, message, from_email, recipient_list)
    if users:
        if obj.uweb:
            uweb_id = obj.uweb.id
            from_email = f"{obj.uweb.username} <{obj.uweb.email}>"
        else:
            uweb_id = 0
            from_email = ""
        send_mass_mail(
            (
                text,
                f"{text}. {obj.META.verbose_name}:\n{obj}\n{obj.desc}",
                from_email,
                (f"{user.username} <{user.email}>",),
            )
            for user in users.values()
            if user.id != uweb_id
        )

    return


post_save.connect(send_email_message, sender=Proj, dispatch_uid="save_proj")
post_save.connect(send_email_message, sender=Sprint, dispatch_uid="save_sprint")
post_save.connect(send_email_message, sender=Task, dispatch_uid="save_task")
post_delete.connect(send_email_message, sender=Proj, dispatch_uid="delete_proj")
post_delete.connect(send_email_message, sender=Sprint, dispatch_uid="delete_sprint")
post_delete.connect(send_email_message, sender=Task, dispatch_uid="delete_task")
