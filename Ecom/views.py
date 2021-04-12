from django.contrib.auth import login
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def index(request):
    return HttpResponse("Hiii")

@login_required
def Home(request):
    return render(request, "home.html", {})