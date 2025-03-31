from django.shortcuts import render
from django.http import HttpResponse
import requests
from plotly.offline import plot

from main.add_env.News_data import news_data
from main.add_env.News_ind import ind

from django.core.cache import cache
from celery import shared_task

import json

# Create your views here.



def korea_api(request,unit,id):
    url = "https://api.stock.naver.com/chart/domestic/item/"+id+"?periodType="+unit+"Candle"
    r = requests.get(url, headers={'Content-Type': 'application/json','User-Agent':'Guzzle HTTP Client'})
    return HttpResponse(r)

def korea_stock_list(request):
    url = "https://m.stock.naver.com/api/stocks/marketValue/KOSPI?page=1&pageSize=4"
    r = requests.get(url, headers={'Content-Type': 'application/json','User-Agent':'Guzzle HTTP Client'})
    return HttpResponse(r)

def korea_stock_price(request,id):
    url = "https://m.stock.naver.com/api/stock/"+id+"/askingPrice"
    r = requests.get(url, headers={'Content-Type': 'application/json','User-Agent':'Guzzle HTTP Client'})
    return HttpResponse(r)

def korea_stock_basic(request,id):
    url = "https://m.stock.naver.com/api/stock/"+id+"/basic"
    r = requests.get(url, headers={'Content-Type': 'application/json','User-Agent':'Guzzle HTTP Client'})
    return HttpResponse(r)


def get_or_set_cache(key, func,second):
    data = cache.get(key)
    if data is None:
        data = func()
        cache.set(key, data, second)
    return data


