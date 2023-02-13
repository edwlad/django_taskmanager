from rest_framework import serializers
from app_task.models import Proj, Sprint, Task, TaskStep

# from django.contrib.auth import get_user_model


class NonModelSerializer(serializers.Serializer):
    """Сериализатор с не-модельными полями."""


class ProjSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proj
        fields = "__all__"
        # fields = read_only_fields + ("id", "name", "date_beg", "date_end", "date_max")
        # fields = tuple(v.attname for v in Proj._meta.fields)
        # read_only_fields = fields


class SprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        # fields = "__all__"
        fields = tuple(v.attname for v in Sprint._meta.fields)
        read_only_fields = fields


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        # fields = "__all__"
        fields = tuple(v.attname for v in Task._meta.fields)
        read_only_fields = fields


class TaskStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStep
        fields = "__all__"
