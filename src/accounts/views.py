from django.shortcuts import render, HttpResponse
from django.views import View

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

# Create your views here.

class Test(View):
    def get(self, request):
        return render(request, "index.html", {
            "room_name":"broadcast"
            
            })
