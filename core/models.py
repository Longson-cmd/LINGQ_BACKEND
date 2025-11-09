# Import necessary modules from Django
from django.db import models
from django.contrib.auth.models import User

# Import datetime helpers to handle time calculations
from datetime import timedelta
from django.utils import timezone


# ----------------------------
# Customer Profile Model
# ----------------------------
class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    is_paying_customer = models.BooleanField(default=False)

    paid_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {'Paying' if self.is_paying_customer == True else 'Free'}"
    
    def activate_monthly_payment(self):
        self.is_paying_customer = True

        self.paid_until = timezone.now() + timedelta(days=30)

        self.save()

        print(f"activated monthly payment!")
    
    def check_status(self):
        if self.paid_until:
            if self.paid_until <= timezone.now():
                self.is_paying_customer = False
                self.save()
                print("This is a expired account!")
            else:
                print(f"This a paying customer until {self.paid_until}")
        else:
            print("This is a free account")

 
def upload_text_path(instance, filename):
    return f"documents/{instance.lesson.user.username}/{filename}"

def upload_audio_path(instance, filename):
    return f"audios/{instance.lesson.user.username}/{filename}"

def upload_whisper_result(instance, filename):
    return f"whisper/{instance.lesson.user.username}/{filename}"

def timestamp_path(instance, filename):
    return f"timestamps/{instance.user.username}/{filename}"


class Lessons(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson_name = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    timestamp_file = models.FileField(upload_to=timestamp_path, null=True, blank=True)
  
    def __str__(self):
        return self.lesson_name
    
class UploadedAudios(models.Model):
    lesson = models.ForeignKey(Lessons, on_delete=models.CASCADE)

    has_audio = models.BooleanField(default=False)

    has_whisper_result = models.BooleanField(default=False)

    file_name = models.CharField(max_length=255,  null = True, blank=True)

    file = models.FileField(upload_to=upload_audio_path,  null = True, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    whisper_file_name = models.CharField(max_length=255, null = True, blank=True)

    whisper_file = models.FileField(upload_to=upload_whisper_result, null = True, blank=True)

    def __str__(self):
        return self.file_name or "No file name"

class UploadedText(models.Model):
    lesson = models.ForeignKey(Lessons, on_delete= models.CASCADE)

    file_name = models.CharField(max_length=255)

    file = models.FileField(upload_to=upload_text_path)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name
    



class Words(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)

    word_key = models.CharField(max_length=50)

    word_status = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.word_key}"
    
class Word_Meanings(models.Model):
    word = models.ForeignKey(Words, on_delete= models.CASCADE)

    meaning = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.word} - {self.meaning[:20]}"
    

class Word_Tags(models.Model):
    word = models.ForeignKey(Words, on_delete=models.CASCADE)

    tag = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.word} - {self.tag}"

class Phrases(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    phrase = models.CharField(max_length=100)

    phrase_status = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.phrase}"
    
class Phrase_Meanings(models.Model):
    phrase = models.ForeignKey(Phrases, on_delete=models.CASCADE)

    meaning = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.phrase} - {self.meaning[:20]}"
    
class Phrase_Tags(models.Model):
    phrase = models.ForeignKey(Phrases, on_delete=models.CASCADE)

    tag = models.CharField(max_length=20)

    

    def __str__(self):
        return f"{self.phrase} - {self.tag}"
