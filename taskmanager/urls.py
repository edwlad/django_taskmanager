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
from django.urls import path, re_path, include
from app_task.views import error, Index
from django.contrib.auth.views import LoginView, LogoutView

# from django.http.response import HttpResponseRedirect
# from django.views.generic import TemplateView


urlpatterns = [
    path(
        "",
        Index.as_view(),
        kwargs={"oper": "list", "model": "tasks", "pk": 0},
        name="index",
    ),
    path("api/", include("api_task.urls"), name="api"),
    path("api-auth/", include("rest_framework.urls"), name="api-auth"),
    path("admin/", admin.site.urls, name="admin"),
    # path("accounts/", include("django.contrib.auth.urls")),
    path(
        "login/",
        LoginView.as_view(template_name="login.html"),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("<str:oper>/<str:model>/<int:pk>/", Index.as_view(), name="oper"),
    path(
        "add/<str:model>/",
        Index.as_view(),
        kwargs={"oper": "add", "pk": -1},
        name="add",
    ),
    path(
        "<str:model>/<int:pk>/",
        Index.as_view(),
        kwargs={"oper": "detail"},
        name="detail",
    ),
    path("<str:model>/", Index.as_view(), {"oper": "list", "pk": 0}, name="list"),
    re_path(r".+", error, kwargs={"title": "Не найдено", "status": 404}),
]
