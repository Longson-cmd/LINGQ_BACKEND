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

def upload_course_file(instance, filename):
    return f"{instance.user.username}/{filename}"
    
class Courses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    course_name = models.CharField(max_length=100)

    last_open_at = models.DateTimeField(null = True, blank=True)

    course_img_file = models.FileField(upload_to= upload_course_file, null = True, blank=True)

    def __str__(self):
        return self.course_name
    
def upload_lesson_file(instance, filename):
    return f"{instance.course.user.username}/{filename}"

class Lessons(models.Model):
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)


    lesson_name = models.CharField(max_length=100)

    last_open_at = models.DateTimeField(null = True, blank=True)

    youtube_url = models.CharField(max_length=255, null = True, blank=True)

    text_file = models.FileField(upload_to=upload_lesson_file)

    lesson_img_file = models.FileField(upload_to=upload_lesson_file, null=True, blank=True)

    has_audio = models.BooleanField(default=False)

    audio_file = models.FileField(upload_to=upload_lesson_file, null=True, blank=True)

    has_timestamp = models.BooleanField(default=False)

    whisper_file = models.FileField(upload_to=upload_lesson_file, null=True, blank=True)

    timestamp_file = models.FileField(upload_to=upload_lesson_file, null=True, blank=True)

    def __str__(self):
        return self.lesson_name
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["course", 'lesson_name'], name= 'uniq_course_lesson_name')
        ]


class Words(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)

    updated_at = models.DateTimeField(auto_now=True)  # 👈 important

    word_key = models.CharField(max_length=50)

    word_status = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.word_key}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'word_key'], name = "uniqu_words_word_word_key")
        ]
    
class Word_Meanings(models.Model):
    word = models.ForeignKey(Words, on_delete= models.CASCADE)

    meaning = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.word} - {self.meaning[:20]}"
    class Meta: 
        constraints = [
            models.UniqueConstraint(fields=['word', 'meaning'], name="uniq_word_word_meaning")
        ]
    

class Word_Tags(models.Model):
    word = models.ForeignKey(Words, on_delete=models.CASCADE)

    tag = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.word} - {self.tag}"
    
    class Meta: 
        constraints = [
            models.UniqueConstraint(fields= ['word', 'tag'], name="uniq_word_tag")
        ]

class Phrases(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    phrase = models.CharField(max_length=100)

    phrase_status = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.phrase}"
    
    class Meta:
        constraints= [
            models.UniqueConstraint(fields= ['user', 'phrase'], name = "uniq_phrase_user_phrase")
        ]

    
class Phrase_Meanings(models.Model):
    phrase = models.ForeignKey(Phrases, on_delete=models.CASCADE)

    meaning = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.phrase} - {self.meaning[:20]}"
    
    class Meta:
        constraints= [
            models.UniqueConstraint(fields = ["phrase", "meaning"], name= "uniq_phrase_meaning")
        ]
    
class Phrase_Tags(models.Model):
    phrase = models.ForeignKey(Phrases, on_delete=models.CASCADE)

    tag = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.phrase} - {self.tag}"
    
    class Meta:
        constraints= [
            models.UniqueConstraint(fields = ['phrase', 'tag'], name = "uniq_phrase_tag")
        ]
