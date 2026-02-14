from django.contrib.auth.models import User
from core.models import CustomerProfile, Lessons, Courses
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import os
from django.conf import settings
import shutil

@receiver(post_save, sender = User)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        CustomerProfile.objects.create(user = instance)

@receiver(post_delete, sender = Lessons)
def delete_attached_file(sender, instance, **kwargs):
    if instance.text_file and os.path.isfile(instance.text_file.path):
        os.remove(instance.text_file.path)
    if instance.audio_file and os.path.isfile(instance.audio_file.path):
        os.remove(instance.audio_file.path)
    if instance.whisper_file and os.path.isfile(instance.whisper_file.path):
        os.remove(instance.whisper_file.path)
    if instance.timestamp_file and os.path.isfile(instance.timestamp_file.path):
        os.remove(instance.timestamp_file.path)
    if instance.lesson_img_file and os.path.isfile(instance.lesson_img_file.path):
        os.remove(instance.lesson_img_file.path)
    
@receiver(post_delete, sender = Courses)
def delete_attached_course_img(sender, instance, **kwargs):
    if instance.course_img_file and os.path.isfile(instance.course_img_file.path):
        os.remove(instance.course_img_file.path)
    
@receiver(post_delete, sender= User)
def delete_attached_folder(sender, instance, **kwargs):
    user_dir_path = os.path.join(settings.MEDIA_ROOT, instance.username)
    if os.path.isdir(user_dir_path):
        shutil.rmtree(user_dir_path)
    
