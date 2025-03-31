from django.shortcuts import render
from django.http import HttpResponse
import requests


def index(request):
    return render(request,"main/index_homepage.html")

def index2_simulator(request):
    return render(request,"main/index2_simulator.html")

def index3_strategy(request):
    return render(request,"main/index3_strategy.html")

def index4_user_market(request):
    return render(request,"main/index4_user_market.html")

def chat_return(request): #채팅을 리턴
    data = request.POST.get("message")
    print(data,'채팅창에 입력된 문자')
    return HttpResponse(data)