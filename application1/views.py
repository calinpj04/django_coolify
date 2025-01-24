from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from discord import SyncWebhook
import json

# Create your views here.
def home(request):
    print(request)
    return HttpResponse("hello girlie")

def home2(request):
    return render(request, "home.html")

@csrf_exempt
def kofi(request):   
    form_data = json.loads(request.data)
    print(form_data)

    webhook = SyncWebhook.from_url('https://discord.com/api/webhooks/1331777737479946290/QhAnInypymU_xMpNcXI124FHJ8iI_hKnBk7zarwcL1y3omGU8w6EDK1XRjjbUsh8brJj') # Initializing webhook
    webhook.send(content=form_data) # Executing webhook.

    return JsonResponse({})