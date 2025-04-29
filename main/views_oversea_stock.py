
from django.http import HttpResponse
from django.http import JsonResponse
import datetime

import sys
import os

'''
# 현재 파일의 경로를 기준으로 이전 경로를 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('../')
from a_korea_invest_api_env import get_ovsstk_chart_price
'''

# 시각화및 저장,계산
import pandas as pd
import numpy as np

# 정규화 및 전처리 계산
import requests
import glob
import json



# Create your views here.

def get_file_path(symbol,minute):
    # 현재 실행 중인 파일의 절대 경로
    current_file_path = os.path.abspath(__file__)

    # 현재 파일의 디렉토리 경로
    current_dir = os.path.dirname(current_file_path)

    # 목표 파일 상대 경로
    relative_path = f'../../a_FRDdata_api/price_real_data/real_data_{symbol}_{minute}.json'

    # 목표 파일 절대 경로 계산
    absolute_path = os.path.abspath(os.path.join(current_dir, relative_path))

    return absolute_path

def get_news_file_path():
    # 현재 실행 중인 파일의 절대 경로
    current_file_path = os.path.abspath(__file__)

    # 현재 파일의 디렉토리 경로
    current_dir = os.path.dirname(current_file_path)

    # 목표 파일 상대 경로
    relative_path = f'../../a_News_FRED_data_api/raw_data/total_web_realdata.csv'

    # 목표 파일 절대 경로 계산
    absolute_path = os.path.abspath(os.path.join(current_dir, relative_path))

    return absolute_path

def oversea_api(request, minute, symbol, exchange_code):   # 가격 데이터 호출
    path = get_file_path(symbol, minute)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data_res = data.get('response')  # 로드된 데이터 출력
    data_list = data_res['data']
    return JsonResponse({'status': True, 'response': {'data': data_list}}, status=200)

def oversea_news(request):
    path = get_news_file_path()
    data = pd.read_csv(path)
    return JsonResponse({'status': True, 'response': {'data': data}}, status=200)

def oversea_news(request):
    # CSV 파일 경로 가져오기
    path = get_news_file_path()

    # CSV 파일 읽기
    data = pd.read_csv(path)
    data.fillna('.', inplace=True)

    # DataFrame을 딕셔너리로 변환 (JSON 직렬화 가능)
    data_dict = data.to_dict(orient='records')  # 각 행을 딕셔너리로 변환

    # JsonResponse로 반환
    return JsonResponse({'status': True, 'response': {'data': data_dict}}, status=200)


def oversea_stock_list(request): #전체
    stocks = [
        #나스닥
        {'stockName': '애플 /(Apple Inc.)', 'itemCode': 'AAPL', 'closePrice': 175.00, 'fluctuationsRatio': 0.3, 'exchange_code':'NAS'},
        {'stockName': '마이크로소프트 / (Microsoft Corporation)', 'itemCode': 'MSFT', 'closePrice': 300.00, 'fluctuationsRatio': 0.8, 'exchange_code':'NAS'},
        {'stockName': '아마존 / (Amazon.com Inc.)', 'itemCode': 'AMZN', 'closePrice': 120.00, 'fluctuationsRatio': -0.5, 'exchange_code':'NAS'},
        {'stockName': '구글 / (GOOGL)', 'itemCode': 'GOOGL', 'closePrice': 2800.00, 'fluctuationsRatio': 1.5, 'exchange_code':'NAS'},
        {'stockName': '메타 / Meta Platforms Inc.', 'itemCode': 'META', 'closePrice': 350.00, 'fluctuationsRatio': 1.2, 'exchange_code':'NAS'},
        {'stockName': '엔비디아 / NVIDIA Corporation', 'itemCode': 'NVDA', 'closePrice': 220.00, 'fluctuationsRatio': 0.9, 'exchange_code':'NAS'},
        {'stockName': '테슬라 / Tesla Inc.', 'itemCode': 'TSLA', 'closePrice': 700.00, 'fluctuationsRatio': -2.0, 'exchange_code':'NAS'},
        {'stockName': '페이팔 / PayPal Holdings Inc.', 'itemCode': 'PYPL', 'closePrice': 75.00, 'fluctuationsRatio': -1.0, 'exchange_code':'NAS'},
        {'stockName': '어도비 / Adobe Inc.', 'itemCode': 'ADBE', 'closePrice': 500.00, 'fluctuationsRatio': 1.1, 'exchange_code':'NAS'},
        {'stockName': '넷플릭스 / Netflix Inc.', 'itemCode': 'NFLX', 'closePrice': 450.00, 'fluctuationsRatio': 0.4, 'exchange_code':'NAS'},
        {'stockName': 'SPDR S&P 500 ETF Trust', 'itemCode': 'SPY', 'closePrice': 450.00, 'fluctuationsRatio': 0.5, 'exchange_code':'NAS'},

        # 뉴욕
        {'stockName': 'S&P 3배 ETF/ ProShares Ultra S&P500', 'itemCode': 'UPRO', 'closePrice': 50.00, 'fluctuationsRatio': -1.2, 'exchange_code':'NYS'},
        {'stockName': 'NAS ETF / Invesco QQQ Trust', 'itemCode': 'QQQ', 'closePrice': 370.00, 'fluctuationsRatio': 1.0, 'exchange_code':'NYS'},
        {'stockName': 'NAS 3배 ETF / ProShares Ultra QQQ', 'itemCode': 'TQQQ', 'closePrice': 100.00, 'fluctuationsRatio': 2.5, 'exchange_code':'NYS'},
        {'stockName': '애플 / Apple Inc.', 'itemCode': 'AAPL', 'closePrice': 175.00, 'fluctuationsRatio': 0.3, 'exchange_code':'NYS'},
        {'stockName': '아마존 / Amazon.com Inc.', 'itemCode': 'AMZN', 'closePrice': 120.00, 'fluctuationsRatio': -0.5, 'exchange_code':'NYS'},
        {'stockName': '구글 / Alphabet Inc. (GOOGL)', 'itemCode': 'GOOGL', 'closePrice': 2800.00, 'fluctuationsRatio': 1.5, 'exchange_code':'NYS'},
        {'stockName': '마이크로소프트 / Microsoft Corporation', 'itemCode': 'MSFT', 'closePrice': 300.00, 'fluctuationsRatio': 0.8, 'exchange_code':'NYS'},
        {'stockName': '메타 / Meta Platforms Inc.', 'itemCode': 'META', 'closePrice': 350.00, 'fluctuationsRatio': 1.2, 'exchange_code':'NYS'},
        {'stockName': '엔비디아 / NVIDIA Corporation', 'itemCode': 'NVDA', 'closePrice': 220.00, 'fluctuationsRatio': 0.9, 'exchange_code':'NYS'},
        {'stockName': 'TSMC / Taiwan Semiconductor Manufacturing Company', 'itemCode': 'TSM', 'closePrice': 100.00,'fluctuationsRatio': 0.4, 'exchange_code':'NYS'},

        #아멕스
        {'stockName': '포드 /Ford Motor Company', 'itemCode': 'F', 'closePrice': 12.50, 'fluctuationsRatio': 0.5, 'exchange_code':'AMS'},
        {'stockName': '아메리칸 항공 그룹 / American Airlines Group Inc.', 'itemCode': 'AAL', 'closePrice': 18.30, 'fluctuationsRatio': 1.2, 'exchange_code':'AMS'},
        {'stockName': '제너럴 일렉트릭 / General Electric Company', 'itemCode': 'GE', 'closePrice': 95.20, 'fluctuationsRatio': 0.7, 'exchange_code':'AMS'},
        {'stockName': '델타 항공 / Delta Air Lines Inc.', 'itemCode': 'DAL', 'closePrice': 40.00, 'fluctuationsRatio': 0.9, 'exchange_code':'AMS'},
        {'stockName': '코카콜라 / Coca-Cola Company', 'itemCode': 'KO', 'closePrice': 60.00, 'fluctuationsRatio': 0.4, 'exchange_code':'AMS'},
        {'stockName': '보잉 / Boeing Company', 'itemCode': 'BA', 'closePrice': 220.00, 'fluctuationsRatio': -0.3, 'exchange_code':'AMS'},
        {'stockName': '월마트 / Walmart Inc.', 'itemCode': 'WMT', 'closePrice': 140.00, 'fluctuationsRatio': 0.6, 'exchange_code':'AMS'},
        {'stockName': '체번 / Chevron Corporation', 'itemCode': 'CVX', 'closePrice': 160.00, 'fluctuationsRatio': 1.0, 'exchange_code':'AMS'},
        {'stockName': '엑슨모빌 / Exxon Mobil Corporation', 'itemCode': 'XOM', 'closePrice': 110.00, 'fluctuationsRatio': -0.5, 'exchange_code':'AMS'},
        {'stockName': '화이자 / Pfizer Inc.', 'itemCode': 'PFE', 'closePrice': 45.00, 'fluctuationsRatio': 0.8, 'exchange_code':'AMS'},
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








# Django views.py 예시
import sys
from django.http import JsonResponse
from django.conf import settings

target_path = r"D:\AI_pycharm\pythonProject\3_AI_LLM_finance\a_korea_invest_api_env"
if target_path not in sys.path:
     sys.path.append(target_path)
# --------------------------------------------------------------------
import get_ovsstk_chart_price # 실제 스크립트 파일 이름

def get_realtime_candle_data(request, market, symbol):
    """최신 1분봉 캔들 데이터 1개를 반환하는 API 뷰"""
    try:
        access_token, access_token_expired = get_ovsstk_chart_price.get_access_token()  # 토큰 갱신
        latest_candle_data_list = get_ovsstk_chart_price.fetch_and_save_data(
            market, symbol, 1, 50, access_token # 분봉 '1', 개수 '1'
        )

        if latest_candle_data_list and isinstance(latest_candle_data_list, list) and len(latest_candle_data_list) > 0:
            # 가장 최신 데이터 (리스트의 마지막 요소일 수 있음, 혹은 첫 요소 - 함수 구현 확인)
            latest_candle = latest_candle_data_list[-1] # 마지막 요소 가정

            # 필요한 데이터만 포함하여 반환 (JavaScript에서 사용할 형식과 유사하게)
            response_data = {
                'success': True,
                'data': {
                    'localDate': latest_candle.get('localDate'),
                    'openPrice': latest_candle.get('openPrice'),
                    'highPrice': latest_candle.get('highPrice'),
                    'lowPrice': latest_candle.get('lowPrice'),
                    'closePrice': latest_candle.get('closePrice'),
                    'volume': latest_candle.get('volume')
                }
            }
            return JsonResponse(response_data)
        else:
            # 데이터가 없거나 형식이 잘못된 경우
            return JsonResponse({'success': False, 'error': 'No data received or invalid format'}, status=404)

    except ImportError as e:
         print(f"Import Error: {e}") # 서버 로그에 출력
         return JsonResponse({'success': False,'error': f'Server configuration error: {e}'}, status=500)
    except Exception as e:
        print(f"Error fetching realtime candle: {e}") # 서버 로그에 출력
        # 실제 운영 시에는 더 상세한 오류 로깅 및 처리 필요
        return JsonResponse({'success': False, 'error': f'An error occurred: {e}'}, status=500)













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




