from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.files import File
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from core.models import Lessons, Courses
import os
from utils.handle_upload_text_file import convert_input_to_text
from utils.extract_data import get_lists_from_text
import json


course_names = [
    "IELTS Speaking Foundations",
    "IELTS Speaking Part 1 Mastery",
    "IELTS Speaking Part 2 Strategies",
    "IELTS Speaking Part 3 Thinking Skills",
    "Grammar for Natural Speaking",
    "Vocabulary for Everyday IELTS",
    "Fluency and Pronunciation Training",
    "Confidence Building for Speaking Tests",
    "Common IELTS Speaking Mistakes",
    "Advanced Speaking Band 7+"
]

lesson_names = [
    "Introduction to Daily Conversation",
    "Common IELTS Speaking Topics",
    "Describing People and Places",
    "Expressing Opinions Clearly",
    "Talking About Past Experiences",
    "Future Plans and Ambitions",
    "Handling Abstract Questions",
    "Using Examples in Answers",
    "Improving Fluency and Coherence",
    "Common Grammar Mistakes in Speaking"
]

# lesson_img_path = r"C:\Users\PC\Desktop\practise\lingq\test\lesson.jpg"
# course_img_path = r"C:\Users\PC\Desktop\practise\lingq\test\course.jpg"
lesson_img_path = os.path.join(settings.BASE_DIR, 'test', 'lesson.jpg')
course_img_path = os.path.join(settings.BASE_DIR, 'test', 'course.jpg')




def get_text_file_path(file_name):
    return os.path.join(settings.BASE_DIR, 'test', file_name)

def create_lesson_obj(course, text_file_path,  idx_lesson):
    img_ext = os.path.splitext(lesson_img_path)[1]
    text_ext = '.json'
    lesson_obj = Lessons.objects.create(course = course, lesson_name = lesson_names[idx_lesson], last_open_at = timezone.now())
    with open(lesson_img_path, 'rb') as f:
        lesson_obj.lesson_img_file.save(f'lesson_{idx_lesson}{img_ext}', File(f), save=True)

    with open(text_file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    list_ref, list_id = get_lists_from_text(text)
    json_data = {"list_ref": list_ref, "list_id" : list_id}
    json_bytes = json.dumps(json_data, ensure_ascii=False, indent=2).encode('utf-8')
    json_file = ContentFile(json_bytes)

    lesson_obj.text_file.save(f'text_{idx_lesson}{text_ext}', json_file, save = True)

def create_couser_obj(user, idx_couse):
    course_obj = Courses.objects.create(user = user, course_name = course_names[idx_couse], last_open_at = timezone.now())
    img_ext = os.path.splitext(course_img_path)[1]
    with open(course_img_path, 'rb') as f:
        course_obj.course_img_file.save(f'couser_{idx_couse}{img_ext}', File(f), save = True)
    return course_obj

class Command(BaseCommand):
    help = "Create lessons and course for test@example.com"

    def handle(self, *args, **options):    
        try:
            first_user = User.objects.get(username = 'test@example.com')
        except User.DoesNotExist:
            first_user = User.objects.create_user(
                username = 'test@example.com',
                email = 'test@example.com',
                password = "1234abcd"
            )

        if Courses.objects.filter(user = first_user).exists():
            print("First user already imported courses")
            return
        list_file_names = ['test0.txt', 'test1.txt', 'test2.txt', 'test3.txt', 'check.txt']
        # list_file_names = [ 'test0.txt']
        for idx_course in range(3):
        # for idx_course in range(1):
            course_obj = create_couser_obj(first_user, idx_course)
            for idx_lesson, file_name in enumerate(list_file_names):
                text_file_path = get_text_file_path(file_name)
                create_lesson_obj(course_obj, text_file_path, idx_lesson)
            for idx_lesson, file_name in enumerate(list_file_names):
                text_file_path = get_text_file_path(file_name)
                create_lesson_obj(course_obj, text_file_path, idx_lesson + 5)
        
        self.stdout.write(self.style.SUCCESS(
            "Import lessons and course successuffly for first user"
        ))






