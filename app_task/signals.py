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
    # отключение отправки Email при при любой десериализации фикстуры
    # когда raw == True (например при загрузке с помошью loaddata)
    if kwargs.get("raw", False):
        return

    obj = kwargs.get("instance", None)
    created = kwargs.get("created", None)

    # Какая операция
    oper = ""
    if created is None:
        oper += "Удаление"
    elif created:
        oper += "Создание"
    else:
        oper += "Обновление"

    LOG.debug("SIGNAL: {}, obj={}".format(oper, str(obj)[:50]))

    # создание списка адресатов и генерация темы и текста сообщения
    users = {}
    subj = ""
    text = ""
    if sender is not TaskStep and obj.author:
        users.update({obj.author.id: obj.author})
    if sender is Proj:
        subj = f"{oper}. {Proj.META.verbose_name} ({obj.id})"
        text = f"{oper}. {Proj.META.verbose_name}:\n{obj}\n{obj.desc}"
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
        subj = f"{oper}. {Sprint.META.verbose_name} ({obj.id})"
        text = f"{oper}. {Sprint.META.verbose_name}:\n{obj}\n{obj.desc}"
        for v in obj.sprint_tasks.filter(date_end=None):
            if v.author:
                users.update({v.author.id: v.author})
            if v.user:
                users.update({v.user.id: v.user})
    elif sender is Task:
        subj = f"{oper}. {Task.META.verbose_name} ({obj.id})"
        text = f"{oper}. {Task.META.verbose_name}:\n{obj}\n{obj.desc}"
        if obj.user:
            users.update({obj.user.id: obj.user})
        for v in obj.parent_nexts.filter(date_end=None):
            if v.author:
                users.update({v.author.id: v.author})
            if v.user:
                users.update({v.user.id: v.user})
    elif sender is TaskStep and not obj.auto_create:
        subj = (
            f"{oper}. {TaskStep.META.verbose_name}"
            f" для {Task.META.verbose_name_plural} ({obj.task.id})"
        )
        text = (
            f"{oper}. {TaskStep.META.verbose_name}."
            f"\n{Task.META.verbose_name}: {obj.task}"
            f"\n{TaskStep.META.verbose_name}:\n{obj.desc}"
        )
        obj.uweb = obj.task.author
        if obj.task.author:
            users.update({obj.task.author.id: obj.task.author})
        if obj.task.user:
            users.update({obj.task.user.id: obj.task.user})

    if LOG.isEnabledFor(logging.DEBUG):
        LOG.debug("USERS: {}".format(users))

    # перебор списка адресатов и массовая отправка сообщений
    # (subject, message, from_email, recipient_list)
    if users:
        if hasattr(obj, "uweb") and obj.uweb:
            uweb_id = obj.uweb.id
            from_email = f"{obj.uweb.username} <{obj.uweb.email}>"
        else:
            uweb_id = 0
            from_email = ""
        send_mass_mail(
            (subj, text, from_email, (f"{user.username} <{user.email}>",))
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
