from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from utils.handle_upload_text_file import convert_input_to_txt
from core.models import UploadedText, Lessons
from django.core.files.base import ContentFile
import os
from utils.handle_upload_text_file import create_lesson
import json
@csrf_exempt
def upload_text(request):
    if request.method == "POST":
       
        lesson_name = request.POST.get("lesson_name")
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return JsonResponse({'error': 'No file uploaded'}, status=400)

        try:
            text = convert_input_to_txt(uploaded_file)
        except ValueError as e:
            return JsonResponse({"message" : str(e)})
        
        txt_file_name = os.path.splitext(uploaded_file.name)[0] + "txt"
        txt_file = ContentFile(text.encode("utf-8"), name=txt_file_name)

        lesson, created = Lessons.objects.get_or_create(user = request.user, lesson_name = lesson_name)
        # Replace existing UploadedText for this lesson
        UploadedText.objects.filter(lesson=lesson).delete()

        record = UploadedText.objects.create(
            lesson = lesson,
            file_name = txt_file_name,
            file = txt_file
        )

        return JsonResponse({
            "message" : f"Uploaded {record.file_name} successfully",
            "file_url" : record.file.url
        })
        
    return JsonResponse({"message" : "Invalid method"}, status = 400)

@csrf_exempt
def get_lesson(request):
    if request.method == "GET":
        lesson_name = json.loads(request.body).get("lesson_name")
