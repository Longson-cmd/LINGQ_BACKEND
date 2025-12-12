from django.http import JsonResponse
from utils.handle_upload_text_file import create_lesson
from django.views.decorators.csrf import csrf_exempt
import json
from core.models import Lessons, UploadedText
import traceback
@csrf_exempt
def get_lesson(request):
    if request.method != "GET":
        return JsonResponse({"message" : "Invalid request!"}, status = 400)
    lesson_name = request.GET.get("lesson_name")
    print("lesson_name :", lesson_name)

    try:
        
        lesson = Lessons.objects.get(lesson_name=lesson_name)
        print("get lesson object :",  lesson.lesson_name)
        uploadedtext_obj = UploadedText.objects.get(lesson = lesson)
        print("get uploadedtext object :",  uploadedtext_obj.file_name)

        txt_path = uploadedtext_obj.file.path
        lesson_data, list_sentences = create_lesson(request, txt_path)
        #content as a python list
        return JsonResponse({"lesson_data" : lesson_data, "list_sentences" : list_sentences}, safe=False)
    except Exception as e:
        print("❌ Exception occurred:", e)
        traceback.print_exc()
        return JsonResponse({
            "message": f"There is a problem with getting lesson: {str(e)}"
        }, status=500)