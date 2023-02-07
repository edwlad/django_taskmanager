"""taskmanager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from app_task.views import error, Index
from app_task.models import Proj

from django.http.response import HttpResponseRedirect
from iommi import Table

# from django.views.generic import TemplateView


urlpatterns = [
    path("", Index.as_view(), name="index"),
    # path("", Table(auto__model=Proj, page_size=2).as_view(), name="index"),
    path("detail/<int:pk>/", Index.as_view(), name="detail"),
    path("edit/<int:pk>/", Index.as_view(), name="edit"),
    path("delete/<int:pk>/", Index.as_view(), name="delete"),
    path("add/", Index.as_view(), name="add"),
    path("admin/", admin.site.urls),
    re_path(r"^admin.*", lambda _: HttpResponseRedirect("/admin/")),
    re_path(r".+", error, kwargs={"title": "Не найдено", "status": 404}),
]
