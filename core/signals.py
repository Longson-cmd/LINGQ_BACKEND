from django.contrib.auth.models import User
from core.models import UploadedAudios, UploadedText, CustomerProfile, Lessons
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import os
from django.conf import settings
import shutil

@receiver(post_save, sender = User)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        CustomerProfile.objects.create(user = instance)

@receiver(post_delete, sender = UploadedAudios)
def delete_attached_audio(sender, instance, **kwargs):
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)
    if instance.whisper_file and os.path.isfile(instance.whisper_file.path):
        os.remove(instance.whisper_file.path)

@receiver(post_delete, sender = UploadedText)
def delete_attached_text(sender, instance, **kwargs):
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)

@receiver(post_delete, sender = Lessons)
def detete_attached_lesson_file(sender, instance, **kwargs):
    if instance.timestamp_file and os.path.isfile(instance.timestamp_file.path):
        os.remove(instance.timestamp_file.path)


@receiver(post_delete, sender = User)
def delete_attached_folders(sender, instance, **kwargs):
    user_audio_path = os.path.join(settings.MEDIA_ROOT, f"audios/{instance.username}")
    user_document_path = os.path.join(settings.MEDIA_ROOT, f"documents/{instance.username}")
    user_whisper_path = os.path.join(settings.MEDIA_ROOT, f"whisper/{instance.username}")
    user_timestamp_path = os.path.join(settings.MEDIA_ROOT, f"timestamps/{instance.username}")

    for folder in [user_audio_path, user_document_path, user_whisper_path, user_timestamp_path]:
        if os.path.isdir(folder):
            shutil.rmtree(folder)