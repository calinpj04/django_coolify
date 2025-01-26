import json
import uuid

from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from discord import SyncWebhook

# Create your views here.
def home(request):
    print(request)
    return HttpResponse("hello girlie")

def home2(request):
    return render(request, "home.html")

def kofiemail(request):
    uuid2 = uuid.uuid4()
    uuid_str = str(uuid2)
    print(uuid_str+"Test")
    return render(request, "KofiPurchaseEmail.html")

@csrf_exempt
def kofi(request):   
    form_data = request.POST['data']
    cleaned_form_data = json.loads(form_data)
    print(cleaned_form_data["verification_token"])
    if cleaned_form_data["verification_token"] != "4afd662e-6787-4010-9783-4329d70a36f3":
        return ("Invalid token", 403)
    else:
        print("IS VAILD")
    
    print(form_data)

    webhook = SyncWebhook.from_url('https://discord.com/api/webhooks/1331777737479946290/QhAnInypymU_xMpNcXI124FHJ8iI_hKnBk7zarwcL1y3omGU8w6EDK1XRjjbUsh8brJj') # Initializing webhook
    webhook.send(content=form_data) # Executing webhook.

    return JsonResponse({})