from django.urls import path
from django.contrib import admin
from core.views.auth import register_user, login_user
from core.views.upload_text import upload_text
from core.views.upload_audio import upload_audio, create_timestamp
from core.views.get_lesson import get_lesson
from core.views.update_word import update_word, finish_lesson
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("register/", register_user, name = 'signup'),
    path("login/", login_user, name = 'login'),
    path("upload_text/", upload_text, name = "upload_text"),
    path("upload_audio/", upload_audio, name="upload_audio"),
    path("create_timestamp/" , create_timestamp, name= "create_timestamp"),
    path("get_lesson/" , get_lesson, name= "get_lesson"),
    path("update_word/", update_word, name= "update_word" ),
    path("finish_lesson/",  finish_lesson, name= "finshi_lesson" ),

    path("admin/", admin.site.urls)
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )