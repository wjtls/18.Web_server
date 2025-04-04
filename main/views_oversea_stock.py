
from django.http import HttpResponse
from django.http import JsonResponse
import datetime

import sys
import os

# 현재 파일의 경로를 기준으로 이전 경로를 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from a_korea_invest_api_env import get_ovsstk_chart_price

# 시각화및 저장,계산
import pandas as pd
import numpy as np

# 정규화 및 전처리 계산
import requests
import glob
import json



# Create your views here.

def get_file_path(symbol):
    # 현재 실행 중인 파일의 절대 경로
    current_file_path = os.path.abspath(__file__)

    # 현재 파일의 디렉토리 경로
    current_dir = os.path.dirname(current_file_path)

    # 목표 파일 상대 경로
    relative_path = f'../../a_FRDdata_api/price_real_data/real_data_{symbol}_1m.json'

    # 목표 파일 절대 경로 계산
    absolute_path = os.path.abspath(os.path.join(current_dir, relative_path))

    return absolute_path

def oversea_api(request, minute, symbol, exchange_code):
    path = get_file_path(symbol)
    print('불러오기')
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data_res = data.get('response')  # 로드된 데이터 출력
    data_list = data_res['data']
    return JsonResponse({'status': True, 'response': {'data': data_list}}, status=200)


def oversea_stock_list(request): #전체
    stocks = [
        #나스닥
        {'stockName': '애플 (Apple Inc.)', 'itemCode': 'AAPL', 'closePrice': 175.00, 'fluctuationsRatio': 0.3, 'exchange_code':'NAS'},
        {'stockName': '마이크로소프트 (Microsoft Corporation)', 'itemCode': 'MSFT', 'closePrice': 300.00, 'fluctuationsRatio': 0.8, 'exchange_code':'NAS'},
        {'stockName': '아마존 (Amazon.com Inc.)', 'itemCode': 'AMZN', 'closePrice': 120.00, 'fluctuationsRatio': -0.5, 'exchange_code':'NAS'},
        {'stockName': 'Alphabet Inc. (GOOGL)', 'itemCode': 'GOOGL', 'closePrice': 2800.00, 'fluctuationsRatio': 1.5, 'exchange_code':'NAS'},
        {'stockName': 'Meta Platforms Inc.', 'itemCode': 'META', 'closePrice': 350.00, 'fluctuationsRatio': 1.2, 'exchange_code':'NAS'},
        {'stockName': 'NVIDIA Corporation', 'itemCode': 'NVDA', 'closePrice': 220.00, 'fluctuationsRatio': 0.9, 'exchange_code':'NAS'},
        {'stockName': 'Tesla Inc.', 'itemCode': 'TSLA', 'closePrice': 700.00, 'fluctuationsRatio': -2.0, 'exchange_code':'NAS'},
        {'stockName': 'PayPal Holdings Inc.', 'itemCode': 'PYPL', 'closePrice': 75.00, 'fluctuationsRatio': -1.0, 'exchange_code':'NAS'},
        {'stockName': 'Adobe Inc.', 'itemCode': 'ADBE', 'closePrice': 500.00, 'fluctuationsRatio': 1.1, 'exchange_code':'NAS'},
        {'stockName': 'Netflix Inc.', 'itemCode': 'NFLX', 'closePrice': 450.00, 'fluctuationsRatio': 0.4, 'exchange_code':'NAS'},
        {'stockName': 'SPDR S&P 500 ETF Trust', 'itemCode': 'SPY', 'closePrice': 450.00, 'fluctuationsRatio': 0.5, 'exchange_code':'NAS'},

        # 뉴욕
        {'stockName': 'ProShares Ultra S&P500', 'itemCode': 'UPRO', 'closePrice': 50.00, 'fluctuationsRatio': -1.2, 'exchange_code':'NYS'},
        {'stockName': 'Invesco QQQ Trust', 'itemCode': 'QQQ', 'closePrice': 370.00, 'fluctuationsRatio': 1.0, 'exchange_code':'NYS'},
        {'stockName': 'ProShares Ultra QQQ', 'itemCode': 'TQQQ', 'closePrice': 100.00, 'fluctuationsRatio': 2.5, 'exchange_code':'NYS'},
        {'stockName': 'Apple Inc.', 'itemCode': 'AAPL', 'closePrice': 175.00, 'fluctuationsRatio': 0.3, 'exchange_code':'NYS'},
        {'stockName': 'Amazon.com Inc.', 'itemCode': 'AMZN', 'closePrice': 120.00, 'fluctuationsRatio': -0.5, 'exchange_code':'NYS'},
        {'stockName': 'Alphabet Inc. (GOOGL)', 'itemCode': 'GOOGL', 'closePrice': 2800.00, 'fluctuationsRatio': 1.5, 'exchange_code':'NYS'},
        {'stockName': 'Microsoft Corporation', 'itemCode': 'MSFT', 'closePrice': 300.00, 'fluctuationsRatio': 0.8, 'exchange_code':'NYS'},
        {'stockName': 'Meta Platforms Inc.', 'itemCode': 'META', 'closePrice': 350.00, 'fluctuationsRatio': 1.2, 'exchange_code':'NYS'},
        {'stockName': 'NVIDIA Corporation', 'itemCode': 'NVDA', 'closePrice': 220.00, 'fluctuationsRatio': 0.9, 'exchange_code':'NYS'},
        {'stockName': 'Taiwan Semiconductor Manufacturing Company', 'itemCode': 'TSM', 'closePrice': 100.00,'fluctuationsRatio': 0.4, 'exchange_code':'NYS'},

        #아멕스
        {'stockName': 'Ford Motor Company', 'itemCode': 'F', 'closePrice': 12.50, 'fluctuationsRatio': 0.5, 'exchange_code':'AMS'},
        {'stockName': 'American Airlines Group Inc.', 'itemCode': 'AAL', 'closePrice': 18.30, 'fluctuationsRatio': 1.2, 'exchange_code':'AMS'},
        {'stockName': 'General Electric Company', 'itemCode': 'GE', 'closePrice': 95.20, 'fluctuationsRatio': 0.7, 'exchange_code':'AMS'},
        {'stockName': 'Delta Air Lines Inc.', 'itemCode': 'DAL', 'closePrice': 40.00, 'fluctuationsRatio': 0.9, 'exchange_code':'AMS'},
        {'stockName': 'Coca-Cola Company', 'itemCode': 'KO', 'closePrice': 60.00, 'fluctuationsRatio': 0.4, 'exchange_code':'AMS'},
        {'stockName': 'Boeing Company', 'itemCode': 'BA', 'closePrice': 220.00, 'fluctuationsRatio': -0.3, 'exchange_code':'AMS'},
        {'stockName': 'Walmart Inc.', 'itemCode': 'WMT', 'closePrice': 140.00, 'fluctuationsRatio': 0.6, 'exchange_code':'AMS'},
        {'stockName': 'Chevron Corporation', 'itemCode': 'CVX', 'closePrice': 160.00, 'fluctuationsRatio': 1.0, 'exchange_code':'AMS'},
        {'stockName': 'Exxon Mobil Corporation', 'itemCode': 'XOM', 'closePrice': 110.00, 'fluctuationsRatio': -0.5, 'exchange_code':'AMS'},
        {'stockName': 'Pfizer Inc.', 'itemCode': 'PFE', 'closePrice': 45.00, 'fluctuationsRatio': 0.8, 'exchange_code':'AMS'},
    ]
    return JsonResponse({'stocks': stocks})

def oversea_NASD_stock_list(request):
    stocks = [
        {'stockName': 'Apple Inc.', 'itemCode': 'AAPL', 'closePrice': 175.00, 'fluctuationsRatio': 0.3},
        {'stockName': 'Microsoft Corporation', 'itemCode': 'MSFT', 'closePrice': 300.00, 'fluctuationsRatio': 0.8},
        {'stockName': 'Amazon.com Inc.', 'itemCode': 'AMZN', 'closePrice': 120.00, 'fluctuationsRatio': -0.5},
        {'stockName': 'Alphabet Inc. (GOOGL)', 'itemCode': 'GOOGL', 'closePrice': 2800.00, 'fluctuationsRatio': 1.5},
        {'stockName': 'Meta Platforms Inc.', 'itemCode': 'META', 'closePrice': 350.00, 'fluctuationsRatio': 1.2},
        {'stockName': 'NVIDIA Corporation', 'itemCode': 'NVDA', 'closePrice': 220.00, 'fluctuationsRatio': 0.9},
        {'stockName': 'Tesla Inc.', 'itemCode': 'TSLA', 'closePrice': 700.00, 'fluctuationsRatio': -2.0},
        {'stockName': 'PayPal Holdings Inc.', 'itemCode': 'PYPL', 'closePrice': 75.00, 'fluctuationsRatio': -1.0},
        {'stockName': 'Adobe Inc.', 'itemCode': 'ADBE', 'closePrice': 500.00, 'fluctuationsRatio': 1.1},
        {'stockName': 'Netflix Inc.', 'itemCode': 'NFLX', 'closePrice': 450.00, 'fluctuationsRatio': 0.4},
    ]
    return JsonResponse({'stocks': stocks})


def oversea_NYSE_stock_list(request):
    stocks = [
        {'stockName': 'SPDR S&P 500 ETF Trust', 'itemCode': 'SPY', 'closePrice': 450.00, 'fluctuationsRatio': 0.5}, #close와 ratio는 실시간 현재 값
        {'stockName': 'ProShares Ultra S&P500', 'itemCode': 'UPRO', 'closePrice': 50.00, 'fluctuationsRatio': -1.2},
        {'stockName': 'Invesco QQQ Trust', 'itemCode': 'QQQ', 'closePrice': 370.00, 'fluctuationsRatio': 1.0},
        {'stockName': 'ProShares Ultra QQQ', 'itemCode': 'TQQQ', 'closePrice': 100.00, 'fluctuationsRatio': 2.5},
        {'stockName': 'Apple Inc.', 'itemCode': 'AAPL', 'closePrice': 175.00, 'fluctuationsRatio': 0.3},
        {'stockName': 'Amazon.com Inc.', 'itemCode': 'AMZN', 'closePrice': 120.00, 'fluctuationsRatio': -0.5},
        {'stockName': 'Alphabet Inc. (GOOGL)', 'itemCode': 'GOOGL', 'closePrice': 2800.00, 'fluctuationsRatio': 1.5},
        {'stockName': 'Microsoft Corporation', 'itemCode': 'MSFT', 'closePrice': 300.00, 'fluctuationsRatio': 0.8},
        {'stockName': 'Meta Platforms Inc.', 'itemCode': 'META', 'closePrice': 350.00, 'fluctuationsRatio': 1.2},
        {'stockName': 'NVIDIA Corporation', 'itemCode': 'NVDA', 'closePrice': 220.00, 'fluctuationsRatio': 0.9},
        {'stockName': 'Taiwan Semiconductor Manufacturing Company', 'itemCode': 'TSM', 'closePrice': 100.00, 'fluctuationsRatio': 0.4},
    ]
    return JsonResponse({'stocks': stocks})



def oversea_AMEX_stock_list(request):
    stocks = [
        {'stockName': 'Ford Motor Company', 'itemCode': 'F', 'closePrice': 12.50, 'fluctuationsRatio': 0.5},
        {'stockName': 'American Airlines Group Inc.', 'itemCode': 'AAL', 'closePrice': 18.30, 'fluctuationsRatio': 1.2},
        {'stockName': 'General Electric Company', 'itemCode': 'GE', 'closePrice': 95.20, 'fluctuationsRatio': 0.7},
        {'stockName': 'Delta Air Lines Inc.', 'itemCode': 'DAL', 'closePrice': 40.00, 'fluctuationsRatio': 0.9},
        {'stockName': 'Coca-Cola Company', 'itemCode': 'KO', 'closePrice': 60.00, 'fluctuationsRatio': 0.4},
        {'stockName': 'Boeing Company', 'itemCode': 'BA', 'closePrice': 220.00, 'fluctuationsRatio': -0.3},
        {'stockName': 'Walmart Inc.', 'itemCode': 'WMT', 'closePrice': 140.00, 'fluctuationsRatio': 0.6},
        {'stockName': 'Chevron Corporation', 'itemCode': 'CVX', 'closePrice': 160.00, 'fluctuationsRatio': 1.0},
        {'stockName': 'Exxon Mobil Corporation', 'itemCode': 'XOM', 'closePrice': 110.00, 'fluctuationsRatio': -0.5},
        {'stockName': 'Pfizer Inc.', 'itemCode': 'PFE', 'closePrice': 45.00, 'fluctuationsRatio': 0.8},
    ]
    return JsonResponse({'stocks': stocks})


def oversea_stock_price(request,id):
    url = "https://m.stock.naver.com/api/stock/"+id+"/askingPrice"
    r = requests.get(url, headers={'Content-Type': 'application/json','User-Agent':'Guzzle HTTP Client'})
    return HttpResponse(r)


def total_time_Frame(data, minute,col_name):  # all data 분봉 출력( traning O  , real backtest x , real trading x)

    # 분봉출력: 실시간 시뮬레이터, 학습 = data count 만큼(또는 전체) 를 뽑아서 연산
    #       실전 = 일부만 뽑아서 전체를뽑은것과 같은 분봉이 나와야함

    price_data = data

    if len(data) % minute == 0:
        index_data = [step * minute for step in range(int(np.trunc(len(data) / minute)))]
    else:
        index_data = [step * minute for step in range(int(np.trunc(len(data) / minute)) + 1)]  # 인터벌

    res = pd.DataFrame(price_data).iloc[index_data]

    res = pd.DataFrame(res)
    res.columns= col_name

    return res

def oversea_stock_basic(request,id):
    url = "https://m.stock.naver.com/api/stock/"+id+"/basic"
    r = requests.get(url, headers={'Content-Type': 'application/json','User-Agent':'Guzzle HTTP Client'})
    return HttpResponse(r)




