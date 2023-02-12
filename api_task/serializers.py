from rest_framework import serializers
from app_task.models import Proj, Sprint, Task, TaskStep

# from django.contrib.auth import get_user_model


class NonModelSerializer(serializers.Serializer):
    """Сериализатор с не-модельными полями."""


class ProjSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proj
        fields = "__all__"


class SprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        # read_only_fields = ("date_plan", "days_plan")
        fields = "__all__"
        # fields = tuple(v.attname for v in Task._meta.fields)


class TaskStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStep
        fields = "__all__"
