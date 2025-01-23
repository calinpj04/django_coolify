from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Create your views here.
def home(request):
    print(request)
    return HttpResponse("hello girlie")

def home2(request):
    return render(request, "home.html")

@csrf_exempt
def kofi(request):
     print(request)
     return JsonResponse()