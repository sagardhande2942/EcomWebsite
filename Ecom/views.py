from django.contrib.auth import login
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

def index(request):
    return HttpResponse("Hiii")

@login_required
def Home(request):
    return render(request, "home.html", {})

def redi(request):
    redirect('/auth/')
    return HttpResponse(
        "<h1>Redirecting</h1><script>window.location.href = '/auth/'</script>"
        )