from django.http import JsonResponse
from core.models import Lessons, UploadedAudios, UploadedText
from django.views.decorators.csrf import csrf_exempt
from utils.timestamp import get_sentence_timestamp
from django.core.files.base import ContentFile
import json
@csrf_exempt
def upload_audio(request):
    if request.method == "POST":
        file_type = request.POST.get("file_type")
        lesson_name = request.POST.get("lesson_name")
        uploaded_file = request.FILES.get("file")
        # print(uploaded_file.name)
        if not lesson_name or not uploaded_file:
            return JsonResponse({"message" : "Missing file or lesson name"}, status = 400)
        
        lesson, created = Lessons.objects.get_or_create( user = request.user, lesson_name = lesson_name)
        instance, created = UploadedAudios.objects.get_or_create(lesson = lesson)
        if file_type == "audio":
            instance.file_name = uploaded_file.name
            instance.file = uploaded_file
            instance.has_audio = True
            message = f"Uploaded {instance.file_name} successfully"
            file_url = instance.file.url 
        else:
            instance.whisper_file_name = uploaded_file.name
            instance.whisper_file = uploaded_file
            instance.has_whisper_result = True
            message = f"Uploaded {instance.whisper_file_name} successfully"
            file_url = instance.whisper_file.url
        instance.save()
        return JsonResponse({
            "message" : message,
            "file_url" : file_url
        })

    return JsonResponse({"message" : "Invalid method!"}, status = 400)
import traceback
@csrf_exempt
def create_timestamp(request):
    if request.method != "POST":
        return JsonResponse({"message" : "Invalid request!"}, status = 400)
    data = json.loads(request.body)
    lesson_name = data.get("lesson_name")
    print("🔹 Received lesson_name:", lesson_name)
    print("🔹 Current user:", request.user)

    try:
        lesson = Lessons.objects.get(user=request.user, lesson_name=lesson_name)
        print("✅ Lesson found:", lesson)

        audio = UploadedAudios.objects.get(lesson=lesson)
        print("✅ Audio found:", audio)

        document = UploadedText.objects.get(lesson=lesson)
        print("✅ Text found:", document)

        whisper_path = audio.whisper_file.path
        document_path = document.file.path
        print("📂 whisper_path:", whisper_path)
        print("📂 document_path:", document_path)

    except Exception as e:
        print("❌ Exception occurred:", e)
        traceback.print_exc()
        return JsonResponse({
            "message": f"There is a problem with getting audio & text paths: {str(e)}"
        }, status=400)
    timestamp = get_sentence_timestamp(document_path, whisper_path)
    timestamp_file_name = f"{lesson_name}_timestamp.json"
    # Convert to JSON string
    json_data = json.dumps(timestamp, ensure_ascii=False, indent=2)

    lesson.timestamp_file.save(
        timestamp_file_name,
        ContentFile(json_data.encode("utf-8")),
        save=True
    )

    return JsonResponse({"message" : "Created timestamp successfully!"})