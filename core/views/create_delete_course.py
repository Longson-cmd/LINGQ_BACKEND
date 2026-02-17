from django.http import JsonResponse
from core.models import Courses
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import traceback
import json
@login_required
def create_course(request):
    if request.method != "POST":
        return JsonResponse({"message": " Invalid request!"}, status = 405)
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    course_name = request.POST.get('course_name', "").strip()
    picture_file = request.FILES.get("course_picture")

    if not course_name:
        return JsonResponse({'message' : 'Missing course name!'}, status = 400)
    if Courses.objects.filter(user = request.user, course_name = course_name).exists():
        return JsonResponse({"message": "this course already exists!"}, status = 400)

    course = Courses.objects.create(user = request.user, course_name = course_name)

    if picture_file:
        course.course_img_file.save(picture_file.name, picture_file, save = True)

    return JsonResponse({"message" : f"Creating {course_name} course successfully!"}, status = 201)


@csrf_exempt
def delete_course(request):
    if request.method != 'DELETE':
        return JsonResponse({'message': 'Invalid request!'}, status = 405)
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    data = json.loads(request.body)
    course_name = data.get('course_name', '').strip()
    print('course_name', course_name)
    try:     
        Courses.objects.get(user= request.user, course_name = course_name).delete()
    except Courses.DoesNotExist:
            return JsonResponse(
            {"message": "Course not found"},
            status=404
        )
    return JsonResponse({"message": f"Delete {course_name} course successfully!"}, status = 200)