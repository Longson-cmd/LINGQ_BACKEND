from django.http import JsonResponse
from utils.handle_upload_text_file import create_lesson
from utils.handle_youtube_url import get_timestamp
from utils.extract_data import get_lists_from_text
from utils.handle_upload_text_file import convert_input_to_text
from django.views.decorators.csrf import csrf_exempt
import json
from core.models import Lessons, Courses
import traceback  
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from yt_dlp import YoutubeDL
import requests
import os
from urllib.parse import urlparse

# @login_required
@csrf_exempt
def get_lesson(request):
    if request.method != "GET":
        return JsonResponse({"message" : "Invalid request!"}, status = 405)
    lesson_name = request.GET.get("lesson_name", "").strip()
    course_name = request.GET.get("course_name", "").strip()
    print("CONTENT_TYPE", request.content_type)
    print("GET", request.GET)
    print("USER", request.user)
    if not lesson_name or not course_name:
        return JsonResponse({"message": "Missing lesson name or course name!"}, status = 400)


    try:
        course = Courses.objects.get(user = request.user, course_name = course_name)
        lesson = Lessons.objects.get(course = course ,lesson_name=lesson_name)
        print("get lesson object :",  lesson.lesson_name)
        

        with lesson.text_file.open("rb") as f:
            raw = f.read()

            data = json.loads(raw.decode('utf-8'))
            list_ref = data["list_ref"]
            list_id = data["list_id"]
        lesson.last_open_at = timezone.now()
        lesson.save(update_fields=["last_open_at"])
        course.last_open_at = timezone.now()
        course.save(update_fields=["last_open_at"])
        lesson_data, list_sentences, Tags_Meanings, core_data = create_lesson(request, list_ref, list_id)

        list_timestamp = None
        if lesson.has_timestamp and lesson.timestamp_file and lesson.timestamp_file.name:
            with lesson.timestamp_file.open('rb') as f:
                raw = f.read()
                list_timestamp = json.loads(raw.decode('utf-8'))

        youtube_url = lesson.youtube_url if lesson.youtube_url else ""
        audio_url = lesson.audio_file.url if (lesson.has_audio and lesson.audio_file and lesson.audio_file.name) else ""
        audio_list ={
            "youtube_url": youtube_url,
            "audio_url": audio_url,
        }
        #content as a python list
        return JsonResponse({
            "lesson_data": lesson_data,
            "list_sentences": list_sentences,
            "Tags_Meanings" : Tags_Meanings,
            "audios": audio_list,
            "core_data": core_data,
            "timestamp": list_timestamp 
        },  
        status = 200,
        json_dumps_params={"ensure_ascii": False},
        content_type="application/json; charset=utf-8",)
    

    except Exception as e:
        print("❌ Exception occurred:", e)
        traceback.print_exc()
        return JsonResponse({
            "message": f"There is a problem with getting lesson: {str(e)}"
        }, status=404)
    


@csrf_exempt
@login_required
def delete_lesson(request):
    if request.method != 'POST':
        return JsonResponse({"message" : "Invalid request!"}, status = 405)
    
    data = json.loads(request.body.decode('utf-8') or '{}')
    lesson_name = data.get('lesson_name', '').strip()
    course_name = data.get('course_name', '').strip()
    if not lesson_name or not course_name:
        return JsonResponse({'message': f'Missing required fields'}, status = 400)

    try: 
        course = Courses.objects.get(user = request.user, course_name = course_name)
        lesson_obj = Lessons.objects.get(course = course, lesson_name = lesson_name)
        lesson_obj.delete()
        return JsonResponse({'message': f'Detele {lesson_name} successfully!' }, status = 200)
    except Exception as e:
        print("Exception occurred :", e)
        return JsonResponse({'message': f'There is a problem with deleting {lesson_name} lesson'}, status = 404)



def get_thumbnail_url(url):
    with YoutubeDL({"quiet": True, "no_warnings":True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get("thumbnail")
    

def save_thumbnail_to_lesson(lesson, thumbnail_url):
    response = requests.get(thumbnail_url, timeout=10)
    response.raise_for_status()
    path = urlparse(thumbnail_url).path
    ext = os.path.splitext(path)[1] or ".jpg"
    img_file_name = lesson.lesson_name + "_thumbnail" + ext
    lesson.lesson_img_file.save(
        img_file_name,
        ContentFile(response.content),
        save = True
    )

@csrf_exempt
@login_required
def create_youtube_lesson(request):
    if request.method != "POST":
        return JsonResponse({"message" : "Invalid request !"}, status = 405)
    
    data = json.loads(request.body)
    course_name = data.get("course_name", "default").strip()
    youtube_url = data.get("youtube_url", "").strip()
    lesson_name = data.get("lesson_name", "").strip()
    # print("CONTENT_TYPE", request.content_type)
    # print("REQUEST POST", request.POST)
    if not course_name  or not youtube_url:
        return JsonResponse({"message": "Missing course,  or youtube url"}, status = 400)
 
    # ---------create new lesson----------
    try:
        list_timestamp, json_dict, youtube_id, youtube_title = get_timestamp(youtube_url)
        
    except Exception as e:
        print("Exception occurred: ", e)
        return JsonResponse({
            "message": f"There is a error with downloading youtube subtitles : {str(e)}"
        }, status = 500)
    
    lesson_name = lesson_name if lesson_name else youtube_title
    course , created = Courses.objects.get_or_create(user = request.user, course_name = course_name)
    course.last_open_at = timezone.now()
    course.save(update_fields=['last_open_at'])
    if Lessons.objects.filter(course  = course, lesson_name = lesson_name).exists():
        return JsonResponse({"message": f"lesson {lesson_name} already exists!"}, status = 409 )
    
    try:
        text_file_name = youtube_id + ".json"
        text_file_bytes = json.dumps(json_dict, ensure_ascii= False).encode("utf-8")
        text_file = ContentFile(text_file_bytes)
        
        timestamp_file_name = youtube_id + "_timestamp" + ".json"
        timestamp_file_bytes = json.dumps(list_timestamp, indent=2, ensure_ascii=False).encode("utf-8")
        timestamp_file = ContentFile(timestamp_file_bytes)

        lesson = Lessons.objects.create(course = course, lesson_name = lesson_name, youtube_url = youtube_url, last_open_at = timezone.now())
        lesson.text_file.save(text_file_name, text_file, save = True)
        lesson.timestamp_file.save(timestamp_file_name, timestamp_file, save = True)
    except Exception as e:
        print("Exception occured: ", e)
        # traceback.print_exc()
        return JsonResponse({'message': str(e)}, status = 500)

    thumbnail = get_thumbnail_url(youtube_url)
    if thumbnail:
        save_thumbnail_to_lesson(lesson, thumbnail)
    return JsonResponse({
        "message": "Successfully created new lesson!",
        "lesson_name": lesson_name,
        'course_name': course_name
    },
     status = 200)


@csrf_exempt
@login_required
def create_lesson_manually(request):
    if request.method != "POST":
        return JsonResponse({'message' : 'Invalid request !'}, status = 405)
    
    lesson_name = request.POST.get('lesson_name', "").strip()
    course_name = request.POST.get("course_name", "default").strip()
    input_text = request.POST.get("inputText", "").strip()
    frontend_text_file = request.FILES.get('textfile')
    picture_file = request.FILES.get('picture')
    audio_file = request.FILES.get('audiofile')

    if not lesson_name or (not input_text and not frontend_text_file):
        return JsonResponse({'message' : 'Missing necessary fields!'}, status = 400)
    
    course, created = Courses.objects.get_or_create(user = request.user, course_name = course_name)
    course.last_open_at = timezone.now()
    course.save(update_fields= ['last_open_at'])
    if Lessons.objects.filter(course = course, lesson_name = lesson_name).exists():
        return JsonResponse({"message": 'Lesson already exists!'}, status = 409)
    
    
    try:
        if input_text:
            list_ref, list_id = get_lists_from_text(input_text)
        else:
            text = convert_input_to_text(frontend_text_file)
            list_ref, list_id = get_lists_from_text(text)

        text_file_dict = {"list_ref": list_ref, "list_id" : list_id}
        text_file_bytes = json.dumps(text_file_dict, ensure_ascii=False).encode('utf-8')
        text_file_name = lesson_name.replace(" ", '_') + '.json'
        text_file = ContentFile(text_file_bytes)
    except Exception as e:
        print('Exception occurred: ', e)
        # traceback.print_exc()
        return JsonResponse({'message': str(e)}, status = 500)
    lesson= Lessons.objects.create(course = course, lesson_name = lesson_name, last_open_at = timezone.now())
    lesson.text_file.save(text_file_name, text_file, save = True)


    if picture_file:
        lesson.lesson_img_file.save(picture_file.name, picture_file, save = True)
    if audio_file:
        lesson.audio_file.save(audio_file.name, audio_file, save= True)

    return JsonResponse({
        'message' : f'Create lesson {lesson_name} successfully!',
        "lesson_name": lesson_name,
        "course_name": course_name
    }, status = 200)

    

    










# if input_text:
#         list_ref, list_id = get_lists_from_text(input_text)
# else:
#     text = convert_input_to_text(text_file)
#     list_ref, list_id = get_lists_from_text(text)

# text_file_dict = {"list_ref": list_ref, "list_id": list_id}
# text_file_bytes = json.dump(text_file_dict, ensure_ascii=False).encode('utf-8')
# text_file_name = os.path.splitext(text_file.name)[0] + '.json'
# text_file_json = ContentFile(text_file_bytes)
# lesson.text_file.save(text_file_name, text_file_json, save = True)
