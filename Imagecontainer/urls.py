"""Imagecontainer URL Configuration


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
from django.urls import path
import minios.views as views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('store/', views.store, name= 'store'),
    path('store/<str:name>/', views.object, name='object'),
    path('upload/', views.model_form_upload, name='model_form_upload'),
    path('delete/<str:file_name>/', views.delete, name='delete'),
    path('edit/<str:file_name>/', views.model_form_edit, name='model_form_edit'),
    path('download/<str:file_name>/', views.download, name='download'),
    path('data_update/', views.global_data_update, name='data_update')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)