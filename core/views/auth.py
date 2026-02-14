from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def register_user(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data["email"]
        password = data["password"]
        username = email

        if User.objects.filter(email= email).exists():
            return JsonResponse({"message" : "this account already exists"},  status=400)
        
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password
        )
        return JsonResponse({"message" : "create new account successfully"}, status=200)
    return JsonResponse({"message" : "Invalid method"}, status = 405)


@csrf_exempt
def login_user(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data["email"]
        password = data["password"]

        user = authenticate(request, username= email, password=password)

        if user is not None:
            login(request, user)
            print("current user" , request.user)
            print("session key", request.session.session_key)
            return JsonResponse({"message": "login successfully"})
        return JsonResponse({"message" : "Invalid account"}, status=401)
    return JsonResponse({"message" : "Invalid method"}, status=400)

# Invoke-RestMethod -Method POST "http://localhost:8000/api/register/" `
#   -ContentType "application/json" `
#   -Body '{"email":"test@example.com","password":"1234abcd"}'

