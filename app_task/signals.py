from django.db.models.signals import post_save, post_delete
from app_task.models import Proj, Sprint, Task, TaskStep
from django.core.mail import send_mass_mail
import logging
from django.db.models import Model

LOG = logging.getLogger(__name__)


def send_email_message(sender: Model, **kwargs) -> None:
    """Отправка письма авторам и исполнителям по полученому сигналу от модели.

    Args:
        sender (Model): Модель отправившая сигнал
    """
    obj = kwargs.get("instance", None)
    created = kwargs.get("created", None)

    text = ""
    if created is None:
        text += "Удаление"
    elif created:
        text += "Создание"
    else:
        text += "Обновление"

    LOG.info("SIGNAL: {}, obj={}".format(text, str(obj)[:50]))

    users = {}
    if sender is not TaskStep and obj.author:
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
    elif sender is Task:
        if obj.user:
            users.update({obj.user.id: obj.user})
        for v in obj.parent_nexts.filter(date_end=None):
            if v.author:
                users.update({v.author.id: v.author})
            if v.user:
                users.update({v.user.id: v.user})
    elif sender is TaskStep and not obj.auto_create:
        obj.uweb = obj.task.author
        if obj.task.author:
            users.update({obj.task.author.id: obj.task.author})
        if obj.task.user:
            users.update({obj.task.user.id: obj.task.user})

    if LOG.isEnabledFor(logging.DEBUG):
        LOG.debug("USERS: {}".format(users))

    # (subject, message, from_email, recipient_list)
    if users:
        if hasattr(obj, "uweb") and obj.uweb:
            uweb_id = obj.uweb.id
            from_email = f"{obj.uweb.username} <{obj.uweb.email}>"
        else:
            uweb_id = 0
            from_email = ""
        send_mass_mail(
            (
                f"{text}. {obj.META.verbose_name} ({obj.id})",
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
post_save.connect(send_email_message, sender=TaskStep, dispatch_uid="save_taskstep")
post_delete.connect(send_email_message, sender=Proj, dispatch_uid="delete_proj")
post_delete.connect(send_email_message, sender=Sprint, dispatch_uid="delete_sprint")
post_delete.connect(send_email_message, sender=Task, dispatch_uid="delete_task")
