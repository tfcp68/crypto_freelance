from django.shortcuts import render

# Create your views here.


def switch(request):
    return render(request, "switch/main.html")
