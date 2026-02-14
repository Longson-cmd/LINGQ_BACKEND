from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from utils.handle_upload_text_file import convert_input_to_text
from utils.extract_data import get_lists_from_text

from core.models import  Lessons, Courses
from django.core.files.base import ContentFile
import os
import json
from django.utils import timezone


def generate_unique_filename(course_obj, basename):
    name, ext = os.path.splitext(basename)
    if not Lessons.objects.filter(course = course_obj, lesson_name = name).exists():
        return  f"{name}.json", name
    
    
    counter = 2
    while True:
        new_name = f'{name}_{counter}.json'
        lesson_name = f"{name}_{counter}"
        if not Lessons.objects.filter(course = course_obj, lesson_name = lesson_name).exists():
            return new_name, lesson_name
        
        counter += 1

@csrf_exempt
def upload_text(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request!'}, status = 405)

    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return JsonResponse({'message':'Missing uploaded file!'}, status = 400)
    
    course_obj, created = Courses.objects.get_or_create(user = request.user, course_name = 'Quick import')
    basename = uploaded_file.name 

    text_file_name, lesson_name = generate_unique_filename(course_obj, basename)
    text = convert_input_to_text(uploaded_file)
    list_ref, list_id = get_lists_from_text(text)
    json_data = {'list_ref': list_ref, 'list_id': list_id}
    json_bytes = json.dumps(json_data, ensure_ascii=False).encode('utf-8')
    text_file = ContentFile(json_bytes)

    lesson_obj = Lessons.objects.create(course = course_obj, lesson_name = lesson_name, last_open_at = timezone.now())
    lesson_obj.text_file.save(text_file_name, text_file, save = True)

    return JsonResponse({
        'lesson_name' : lesson_name,
        'course_name' : 'Quick import'
    }, status = 200)
    

@csrf_exempt
def upload_audio(request):
    if request.method != "POST":
        return JsonResponse({"message": "Invalid request"}, status = 405)
    
    course_name = request.POST.get("course_name", "").strip()
    lesson_name = request.POST.get("lesson_name", "").strip()
    uploaded_file = request.FILES.get("file")
    print("CONTENT_TYPE:", request.content_type)
    print("POST:", request.POST)
    print("FILES:", request.FILES)

    if not course_name or not lesson_name or not uploaded_file:
        return JsonResponse({"message": "Missing course_name, lesson_name, or file"}, status = 400)
    
    course, created = Courses.objects.get_or_create(user = request.user, course_name = course_name)
    check_exists_lesson = Lessons.objects.filter(course = course, lesson_name = lesson_name).first()
    if check_exists_lesson and check_exists_lesson.youtube_url:
        return JsonResponse({"message": "Can't change lesson having youtube_url"}, status = 400)

    lesson, created = Lessons.objects.get_or_create(course = course, lesson_name = lesson_name)

    lesson.has_audio = True
    lesson.audio_file.save(uploaded_file.name, uploaded_file, save= True)

    return JsonResponse({
        "message": f"Upload {lesson.audio_file.name} successfully!",
        "file_url": lesson.audio_file.url
    })



