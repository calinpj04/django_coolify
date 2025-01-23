from django.shortcuts import render, HttpResponse

# Create your views here.
def home(request):
    print(request)
    return HttpResponse("hello girlie")

def home2(request):
    return render(request, "home.html")

def kofi(request):
     print(request)