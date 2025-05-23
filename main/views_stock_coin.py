
from django.http import HttpResponse
from django.http import JsonResponse
import datetime

import json
import redis
from django.http import JsonResponse
from django.conf import settings
import traceback

import sys
import os

'''
# 현재 파일의 경로를 기준으로 이전 경로를 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('../')
from a_korea_invest_api_env import get_ovsstk_chart_price
'''
import aiofiles
from typing import Optional, List, Dict, Any
import redis.asyncio as redis
# 시각화및 저장,계산
import pandas as pd
import numpy as np
from django.views.decorators.cache import cache_page, cache_control

# 정규화 및 전처리 계산
import requests
import glob
import json



# Create your views here.

def get_price_file_path(symbol,minute): # 가격 데이터 경로
    # 현재 실행 중인 파일의 절대 경로
    current_file_path = os.path.abspath(__file__)

    # 현재 파일의 디렉토리 경로
    current_dir = os.path.dirname(current_file_path)

    # 목표 파일 상대 경로
    relative_path = f'../../a_FRDdata_api/price_real_data/real_data_{symbol}_{minute}.json'

    # 목표 파일 절대 경로 계산
    absolute_path = os.path.abspath(os.path.join(current_dir, relative_path))

    return absolute_path

def get_past_price_file_path(symbol,minute, data_number): # 과거 가격 데이터 경로
    # 현재 실행 중인 파일의 절대 경로
    current_file_path = os.path.abspath(__file__)

    # 현재 파일의 디렉토리 경로
    current_dir = os.path.dirname(current_file_path)

    # 목표 파일 상대 경로
    relative_path = f'../../a_FRDdata_api/price_past_data/{symbol}/past_data_{symbol}_{minute}_{data_number}.json'

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

def oversea_past_api(request, minute, symbol, data_number):   # 과거 데이터 호출
    file_path_str = get_past_price_file_path(symbol, minute, data_number)

    # 파일 존재 여부 확인 (프로덕션에서는 더 견고한 로깅 및 예외 처리 필요)
    if not os.path.exists(file_path_str) or not os.path.isfile(file_path_str):
        return JsonResponse({'status': False, 'message': f'Data file not found at the specified path: {file_path_str}'}, status=404)

    with open(file_path_str, 'r', encoding='utf-8') as f:
        # 생성된 JSON 파일은 바로 캔들 데이터 리스트임
        candle_data_list = json.load(f)
    # 데이터 형식 검증 (선택적이지만 권장)
    if not isinstance(candle_data_list, list):
        # 예상치 못한 파일 형식일 경우
        return JsonResponse({'status': False, 'message': 'Invalid data format in the file.'}, status=500)
    return JsonResponse({'status': True, 'response': {'data': candle_data_list}}, status=200)

















import redis # <- 동기 라이브러리 사용 확인
import json
from django.http import JsonResponse

# Redis 연결 정보
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

# Redis 연결 풀 생성 (동기 방식 확인)
# redis.asyncio.ConnectionPool 이 아닌 redis.ConnectionPool 사용
redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def get_redis_connection():
  """Redis 커넥션 풀에서 커넥션 가져오기 (동기 방식 확인)"""
  # redis.asyncio.Redis 가 아닌 redis.Redis 사용
  return redis.Redis(connection_pool=redis_pool)

# >>> 캐싱 데코레이터 추가 <<<
@cache_page(1) # 60초(1분) 동안 서버에 이 뷰의 응답을 캐싱
@cache_control(public=True, max_age=1) # 브라우저에게도 60초 동안 캐싱 가능하다고 알림
def load_stock_coin_data(request, minute, symbol, exchange_code): # URL 패턴에 맞는 파라미터 사용 (exchange_code 포함됨)
    """Redis 리스트에서 주식/상품 데이터를 가져오는 뷰 함수 (동기)"""
    data_list = []
    redis_conn = None # finally 블록에서 사용하기 위해 미리 선언 (필수는 아님)
    try:
        # 레디스 연결 가져오기 (동기)
        redis_conn = get_redis_connection()
        redis_key = f"stockdata:{symbol}:{minute}"

        # Redis 리스트에서 모든 요소 가져오기 (동기 lrange)
        # 동기 라이브러리의 lrange는 리스트를 바로 반환함 (코루틴 객체가 아님)
        elements_json = redis_conn.lrange(redis_key, 0, -1) # await 없음!

        if elements_json:
            # 가져온 각 JSON 문자열을 파이썬 딕셔너리로 변환
            for element_json in elements_json: # 이제 에러 없이 반복 가능해야 함
                try:
                    element_dict = json.loads(element_json)
                    data_list.append(element_dict)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON for element in key: {redis_key}, data: {element_json}") # 로깅
        else:
            print(f"Data list is empty or key '{redis_key}' does not exist in Redis.") # 로그

        # API 응답 반환
        return JsonResponse({'status': True, 'response': {'data': data_list}}, status=200)

    # 동기 라이브러리의 예외 처리 사용 확인
    except redis.exceptions.ConnectionError as e:
        print(f"Redis connection error: {e}") # 로깅
        return JsonResponse({'status': False, 'message': 'Failed to connect to Redis'}, status=503)

    except Exception as e:
        # TypeError 등 다른 예외도 여기서 잡힐 수 있음
        print(f"An unexpected error occurred in oversea_api: {e}") # 로깅
        import traceback
        traceback.print_exc() # 개발 중 상세 에러 확인
        return JsonResponse({'status': False, 'message': 'An internal server error occurred'}, status=500)





###################################redis에서 실시간 호가데이터 가져옴#######################
@cache_page(1)
@cache_control(public=True, max_age=1)
def load_stock_coin_ASK_data(request, data_type_or_interval, symbol, exchange_code):  # 파라미터 이름 변경
    """
    Redis에서 주식/코인 데이터를 가져오는 뷰 함수.
    data_type_or_interval이 "ASK"면 호가(문자열), 그 외에는 분봉(리스트)으로 처리.
    """
    redis_conn = None
    response_data = []  # 기본 빈 리스트 (분봉용) 또는 단일 객체 (호가용)

    try:
        redis_conn = get_redis_connection()  # decode_responses=True로 문자열을 받음
        redis_key = f"stockdata:{symbol}:{data_type_or_interval.upper()}"  # data_type도 대문자로 통일


        if not redis_conn.exists(redis_key):
            print(f"DEBUG [views.py]: Key '{redis_key}' does not exist in Redis.")
            return JsonResponse({'status': False, 'message': f"Data for {redis_key} not found in Redis"}, status=404)

        if data_type_or_interval.upper() == "ASK":  # 호가 데이터 (단일 JSON 문자열)
            value_json_str = redis_conn.get(redis_key)
            if value_json_str:
                try:
                    # 단일 JSON 객체를 response_data에 할당 (리스트가 아님)
                    response_data = json.loads(value_json_str)
                    return JsonResponse({'status': True, 'response': {'data': response_data, 'type': 'orderbook'}},
                                        status=200)
                except json.JSONDecodeError:
                    return JsonResponse({'status': False, 'message': 'Error decoding data from Redis'}, status=500)
            else:
                return JsonResponse({'status': False, 'message': f"No data for {redis_key}"}, status=404)

        else:  # K-line (분봉) 데이터 (JSON 문자열의 리스트)
            # K-line 데이터는 바이트로 저장 후 디코딩했으므로, get_redis_connection(decode_responses=False) 필요할 수 있음
            # 하지만 바이낸스 스크립트도 decode_responses=True로 저장했으므로, 여기서는 True로 가정
            elements_json_str_list = redis_conn.lrange(redis_key, 0, -1)

            if elements_json_str_list:
                for element_json_str in elements_json_str_list:
                    try:
                        # 이미 문자열이므로 .decode() 불필요
                        element_dict = json.loads(element_json_str)
                        response_data.append(element_dict)
                    except json.JSONDecodeError:
                        print(
                            f"Error decoding JSON for K-line element in key: {redis_key}, data: {element_json_str[:200]}")
                print(
                    f"DEBUG [views.py]: Successfully fetched and parsed K-line list data for {redis_key} ({len(response_data)} items)")
                return JsonResponse({'status': True, 'response': {'data': response_data, 'type': 'kline_list'}},
                                    status=200)
            else:
                print(f"K-line list for key '{redis_key}' is empty or does not exist.")
                return JsonResponse({'status': False, 'message': f"No K-line data for {redis_key}"}, status=404)

    except redis.exceptions.ConnectionError as e:
        print(f"Redis connection error: {e}")
        return JsonResponse({'status': False, 'message': 'Failed to connect to Redis'}, status=503)
    except redis.exceptions.ResponseError as e_redis_cmd:  # 예: LLEN을 문자열에 사용 시
        print(f"Redis command error for key '{redis_key}': {e_redis_cmd}")
        return JsonResponse({'status': False, 'message': f'Redis data type error for key {redis_key}'}, status=500)
    except Exception as e:
        print(f"An unexpected error occurred in load_stock_coin_data: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': False, 'message': 'An internal server error occurred'}, status=500)
    # finally 블록은 Django 뷰에서 Redis 연결을 자동으로 닫아주므로 필수는 아님 (연결 풀 사용)





















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


def coin_list(requset):
    coins = [
        {'stockName': 'BTC/USDT', 'itemCode': 'BTCUSDT', 'closePrice': 'Binance','fluctuationsRatio': 'Binance', 'exchange_code': 'Binance'},
    ]
    return JsonResponse({'stocks': coins})

def oversea_stock_list(request): #전체
    stocks = [
        # 뉴욕
        {'stockName': 'NAS 3배 ETF', 'itemCode': 'TQQQ', 'closePrice': 'NYS','fluctuationsRatio': 'NYS', 'exchange_code': 'NYS'},
        #{'stockName': 'S&P 3배 ETF/ ProShares Ultra S&P500', 'itemCode': 'UPRO', 'closePrice': 50.00, 'fluctuationsRatio': -1.2, 'exchange_code':'NYS'},
        #{'stockName': 'NAS ETF / Invesco QQQ Trust', 'itemCode': 'QQQ', 'closePrice': 370.00, 'fluctuationsRatio': 1.0, 'exchange_code':'NYS'},
        #{'stockName': '애플 / Apple Inc.', 'itemCode': 'AAPL', 'closePrice': 175.00, 'fluctuationsRatio': 0.3, 'exchange_code':'NYS'},
        #{'stockName': '아마존 / Amazon.com Inc.', 'itemCode': 'AMZN', 'closePrice': 120.00, 'fluctuationsRatio': -0.5, 'exchange_code':'NYS'},
        #{'stockName': '구글 / Alphabet Inc. (GOOGL)', 'itemCode': 'GOOGL', 'closePrice': 2800.00, 'fluctuationsRatio': 1.5, 'exchange_code':'NYS'},
        #{'stockName': '마이크로소프트 / Microsoft Corporation', 'itemCode': 'MSFT', 'closePrice': 300.00, 'fluctuationsRatio': 0.8, 'exchange_code':'NYS'},
        #{'stockName': '메타 / Meta Platforms Inc.', 'itemCode': 'META', 'closePrice': 350.00, 'fluctuationsRatio': 1.2, 'exchange_code':'NYS'},
        #{'stockName': '엔비디아 / NVIDIA Corporation', 'itemCode': 'NVDA', 'closePrice': 220.00, 'fluctuationsRatio': 0.9, 'exchange_code':'NYS'},
        #{'stockName': 'TSMC / Taiwan Semiconductor Manufacturing Company', 'itemCode': 'TSM', 'closePrice': 100.00,'fluctuationsRatio': 0.4, 'exchange_code':'NYS'},

        # 나스닥
        #{'stockName': '애플 /(Apple Inc.)', 'itemCode': 'AAPL', 'closePrice': 175.00, 'fluctuationsRatio': 0.3,'exchange_code': 'NAS'},
        # {'stockName': '마이크로소프트 / (Microsoft Corporation)', 'itemCode': 'MSFT', 'closePrice': 300.00, 'fluctuationsRatio': 0.8, 'exchange_code':'NAS'},
        # {'stockName': '아마존 / (Amazon.com Inc.)', 'itemCode': 'AMZN', 'closePrice': 120.00, 'fluctuationsRatio': -0.5, 'exchange_code':'NAS'},
        #{'stockName': '구글 / (GOOGL)', 'itemCode': 'GOOGL', 'closePrice': 2800.00, 'fluctuationsRatio': 1.5,'exchange_code': 'NAS'},
        #{'stockName': '메타 / Meta Platforms Inc.', 'itemCode': 'META', 'closePrice': 350.00, 'fluctuationsRatio': 1.2,'exchange_code': 'NAS'},
        #{'stockName': '엔비디아 / NVIDIA Corporation', 'itemCode': 'NVDA', 'closePrice': 220.00, 'fluctuationsRatio': 0.9,'exchange_code': 'NAS'},
        #{'stockName': '테슬라 / Tesla Inc.', 'itemCode': 'TSLA', 'closePrice': 700.00, 'fluctuationsRatio': -2.0,'exchange_code': 'NAS'},
        #{'stockName': '페이팔 / PayPal Holdings Inc.', 'itemCode': 'PYPL', 'closePrice': 75.00, 'fluctuationsRatio': -1.0,'exchange_code': 'NAS'},
        #{'stockName': '어도비 / Adobe Inc.', 'itemCode': 'ADBE', 'closePrice': 500.00, 'fluctuationsRatio': 1.1,'exchange_code': 'NAS'},
        #{'stockName': '넷플릭스 / Netflix Inc.', 'itemCode': 'NFLX', 'closePrice': 450.00, 'fluctuationsRatio': 0.4,'exchange_code': 'NAS'},
        #{'stockName': 'SPDR S&P 500 ETF Trust', 'itemCode': 'SPY', 'closePrice': 450.00, 'fluctuationsRatio': 0.5,'exchange_code': 'NAS'},


        #아멕스
        #{'stockName': '포드 /Ford Motor Company', 'itemCode': 'F', 'closePrice': 12.50, 'fluctuationsRatio': 0.5, 'exchange_code':'AMS'},
        #{'stockName': '아메리칸 항공 그룹 / American Airlines Group Inc.', 'itemCode': 'AAL', 'closePrice': 18.30, 'fluctuationsRatio': 1.2, 'exchange_code':'AMS'},
        #{'stockName': '제너럴 일렉트릭 / General Electric Company', 'itemCode': 'GE', 'closePrice': 95.20, 'fluctuationsRatio': 0.7, 'exchange_code':'AMS'},
        #{'stockName': '델타 항공 / Delta Air Lines Inc.', 'itemCode': 'DAL', 'closePrice': 40.00, 'fluctuationsRatio': 0.9, 'exchange_code':'AMS'},
        #{'stockName': '코카콜라 / Coca-Cola Company', 'itemCode': 'KO', 'closePrice': 60.00, 'fluctuationsRatio': 0.4, 'exchange_code':'AMS'},
        #{'stockName': '보잉 / Boeing Company', 'itemCode': 'BA', 'closePrice': 220.00, 'fluctuationsRatio': -0.3, 'exchange_code':'AMS'},
        #{'stockName': '월마트 / Walmart Inc.', 'itemCode': 'WMT', 'closePrice': 140.00, 'fluctuationsRatio': 0.6, 'exchange_code':'AMS'},
        #{'stockName': '체번 / Chevron Corporation', 'itemCode': 'CVX', 'closePrice': 160.00, 'fluctuationsRatio': 1.0, 'exchange_code':'AMS'},
        #{'stockName': '엑슨모빌 / Exxon Mobil Corporation', 'itemCode': 'XOM', 'closePrice': 110.00, 'fluctuationsRatio': -0.5, 'exchange_code':'AMS'},
        #{'stockName': '화이자 / Pfizer Inc.', 'itemCode': 'PFE', 'closePrice': 45.00, 'fluctuationsRatio': 0.8, 'exchange_code':'AMS'},
    ]
    return JsonResponse({'stocks': stocks})

def oversea_NASD_stock_list(request):
    stocks = [
        #{'stockName': 'Apple Inc.', 'itemCode': 'AAPL', 'closePrice': 175.00, 'fluctuationsRatio': 0.3},
        #{'stockName': 'Microsoft Corporation', 'itemCode': 'MSFT', 'closePrice': 300.00, 'fluctuationsRatio': 0.8},
        #{'stockName': 'Amazon.com Inc.', 'itemCode': 'AMZN', 'closePrice': 120.00, 'fluctuationsRatio': -0.5},
        #{'stockName': 'Alphabet Inc. (GOOGL)', 'itemCode': 'GOOGL', 'closePrice': 2800.00, 'fluctuationsRatio': 1.5},
        #{'stockName': 'Meta Platforms Inc.', 'itemCode': 'META', 'closePrice': 350.00, 'fluctuationsRatio': 1.2},
        #{'stockName': 'NVIDIA Corporation', 'itemCode': 'NVDA', 'closePrice': 220.00, 'fluctuationsRatio': 0.9},
        #{'stockName': 'Tesla Inc.', 'itemCode': 'TSLA', 'closePrice': 700.00, 'fluctuationsRatio': -2.0},
        #{'stockName': 'PayPal Holdings Inc.', 'itemCode': 'PYPL', 'closePrice': 75.00, 'fluctuationsRatio': -1.0},
        #{'stockName': 'Adobe Inc.', 'itemCode': 'ADBE', 'closePrice': 500.00, 'fluctuationsRatio': 1.1},
        #{'stockName': 'Netflix Inc.', 'itemCode': 'NFLX', 'closePrice': 450.00, 'fluctuationsRatio': 0.4},
    ]
    return JsonResponse({'stocks': stocks})


def oversea_NYSE_stock_list(request):
    stocks = [
        #{'stockName': 'SPDR S&P 500 ETF Trust', 'itemCode': 'SPY', 'closePrice': 450.00, 'fluctuationsRatio': 0.5}, #close와 ratio는 실시간 현재 값
        #{'stockName': 'ProShares Ultra S&P500', 'itemCode': 'UPRO', 'closePrice': 50.00, 'fluctuationsRatio': -1.2},
        #{'stockName': 'Invesco QQQ Trust', 'itemCode': 'QQQ', 'closePrice': 370.00, 'fluctuationsRatio': 1.0},
        {'stockName': 'NAS 3배 ETF', 'itemCode': 'TQQQ', 'closePrice': 'NYS','fluctuationsRatio': 'NYS', 'exchange_code': 'NYS'},
        #{'stockName': 'Apple Inc.', 'itemCode': 'AAPL', 'closePrice': 175.00, 'fluctuationsRatio': 0.3},
        #{'stockName': 'Amazon.com Inc.', 'itemCode': 'AMZN', 'closePrice': 120.00, 'fluctuationsRatio': -0.5},
        #{'stockName': 'Alphabet Inc. (GOOGL)', 'itemCode': 'GOOGL', 'closePrice': 2800.00, 'fluctuationsRatio': 1.5},
        #{'stockName': 'Microsoft Corporation', 'itemCode': 'MSFT', 'closePrice': 300.00, 'fluctuationsRatio': 0.8},
        #{'stockName': 'Meta Platforms Inc.', 'itemCode': 'META', 'closePrice': 350.00, 'fluctuationsRatio': 1.2},
        #{'stockName': 'NVIDIA Corporation', 'itemCode': 'NVDA', 'closePrice': 220.00, 'fluctuationsRatio': 0.9},
        #{'stockName': 'Taiwan Semiconductor Manufacturing Company', 'itemCode': 'TSM', 'closePrice': 100.00, 'fluctuationsRatio': 0.4},
    ]
    return JsonResponse({'stocks': stocks})



def oversea_AMEX_stock_list(request):
    stocks = [
        #{'stockName': 'Ford Motor Company', 'itemCode': 'F', 'closePrice': 12.50, 'fluctuationsRatio': 0.5},
        #{'stockName': 'American Airlines Group Inc.', 'itemCode': 'AAL', 'closePrice': 18.30, 'fluctuationsRatio': 1.2},
        #{'stockName': 'General Electric Company', 'itemCode': 'GE', 'closePrice': 95.20, 'fluctuationsRatio': 0.7},
        #{'stockName': 'Delta Air Lines Inc.', 'itemCode': 'DAL', 'closePrice': 40.00, 'fluctuationsRatio': 0.9},
        #{'stockName': 'Coca-Cola Company', 'itemCode': 'KO', 'closePrice': 60.00, 'fluctuationsRatio': 0.4},
        #{'stockName': 'Boeing Company', 'itemCode': 'BA', 'closePrice': 220.00, 'fluctuationsRatio': -0.3},
        #{'stockName': 'Walmart Inc.', 'itemCode': 'WMT', 'closePrice': 140.00, 'fluctuationsRatio': 0.6},
        #{'stockName': 'Chevron Corporation', 'itemCode': 'CVX', 'closePrice': 160.00, 'fluctuationsRatio': 1.0},
        #{'stockName': 'Exxon Mobil Corporation', 'itemCode': 'XOM', 'closePrice': 110.00, 'fluctuationsRatio': -0.5},
        #{'stockName': 'Pfizer Inc.', 'itemCode': 'PFE', 'closePrice': 45.00, 'fluctuationsRatio': 0.8},
    ]
    return JsonResponse({'stocks': stocks})


#실시간 모든 심볼의 현재가 호출
# --- Redis 연결 설정 (파일 상단 또는 Django settings.py 기반으로 설정) ---
REDIS_HOST = getattr(settings, 'REDIS_HOST', 'localhost')
REDIS_PORT = getattr(settings, 'REDIS_PORT', 6379)
REDIS_DB_KLINE = getattr(settings, 'REDIS_DB_FOR_KLINES', 0)  # K-line 데이터가 저장된 DB 번호

def get_redis_connection_for_kline_view(decode_responses=False):  # 기본적으로 바이트로 받도록 변경
    """K-line 데이터 조회용 Redis 연결을 반환하는 헬퍼 함수 (동기)"""
    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB_KLINE,
            decode_responses=decode_responses
        )
        r.ping()
        return r
    except redis.exceptions.ConnectionError as e:
        print(f"CRITICAL (views_stock_coin): Redis 연결 실패 - {e}. API가 정상 작동하지 않습니다.")
        return None
    except Exception as e_init:
        print(f"CRITICAL (views_stock_coin): Redis 클라이언트 초기화 중 오류 - {e_init}.")
        return None

def get_realtime_candle_data(request, market, interval, symbol): # 심볼에 해당하는 현재가 호출
    # Redis에서 바이트로 데이터를 읽어와서 직접 디코딩 (check_redis_data.py와 유사하게)
    redis_conn = get_redis_connection_for_kline_view(decode_responses=False)

    if not redis_conn:
        return JsonResponse({'status': False, 'message': 'Redis service unavailable'}, status=503)

    redis_key = f"stockdata:{symbol.upper()}:{interval}"

    print(f"DEBUG [API - get_realtime_candle_data]: Redis 키 조회 시도: '{redis_key}' (Market: {market})")

    try:
        key_type = redis_conn.type(redis_key)  # 키 타입을 바이트로 받음
        if key_type == b'none':  # 바이트 비교
            return JsonResponse(
                {'status': False, 'message': f"No data found for symbol {symbol} with interval {interval}."},
                status=404)
        if key_type != b'list':  # 바이트 비교
            print(f"ERROR [API]: 키 '{redis_key}'는 리스트 타입이 아닙니다 (실제 타입: {key_type.decode('utf-8')}). 저장 방식을 확인하세요.")
            return JsonResponse(
                {'status': False, 'message': f"Invalid data type in Redis for {symbol} [{interval}]. Expected list."},
                status=500)

        last_kline_json_bytes = redis_conn.lindex(redis_key, -1)  # 바이트로 받음

        if last_kline_json_bytes:
            # 바이트를 UTF-8 문자열로 디코딩 후 JSON 파싱
            kline_data = json.loads(last_kline_json_bytes.decode('utf-8'))
            close_price_value = kline_data.get('closePrice')

            if close_price_value is not None:
                try:
                    close_price_float = float(close_price_value)
                    return JsonResponse({
                        'status': True,
                        'symbol': symbol.upper(),
                        'interval': interval,
                        'market': market.upper(),
                        'closePrice': close_price_float,
                        'localDate': kline_data.get('localDate', '')
                    })
                except ValueError:
                    print(f"ERROR [API]: 키 '{redis_key}'의 closePrice ('{close_price_value}')를 float으로 변환 불가.")
                    return JsonResponse(
                        {'status': False, 'message': f"Invalid price data format for {symbol} [{interval}]."},
                        status=500)
            else:
                print(f"WARNING [API]: 키 '{redis_key}'의 마지막 K-line 데이터에 'closePrice' 필드가 없습니다. 데이터: {kline_data}")
                return JsonResponse({'status': False, 'message': f"'closePrice' not found for {symbol} [{interval}]."},
                                    status=404)
        else:
            return JsonResponse({'status': False, 'message': f"Data list empty for {symbol} [{interval}]."}, status=404)

    except redis.exceptions.RedisError as r_err:
        print(f"ERROR [API]: Redis 명령어 실행 중 오류 발생 (키: '{redis_key}'): {r_err}")
        return JsonResponse({'status': False, 'message': 'Error communicating with Redis.'}, status=500)
    except json.JSONDecodeError as j_err:
        data_preview = last_kline_json_bytes.decode('utf-8')[
                       :200] if 'last_kline_json_bytes' in locals() and last_kline_json_bytes else "N/A (bytes)"
        print(f"ERROR [API]: Redis 데이터 JSON 디코딩 실패 (키: '{redis_key}'): {j_err}. 데이터(일부): {data_preview}")
        return JsonResponse({'status': False, 'message': 'Error decoding data from Redis.'}, status=500)
    except Exception as e:
        print(f"ERROR [API]: 알 수 없는 오류 발생 (키: '{redis_key}'): {e}")
        traceback.print_exc()
        return JsonResponse({'status': False, 'message': 'An internal server error occurred.'}, status=500)


@cache_page(1)
@cache_control(public=True, max_age=1)
def get_redis_connection_for_views(decode_responses=False):
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB_KLINE, decode_responses=decode_responses)
        r.ping()
        return r
    except redis.exceptions.ConnectionError as e:
        print(f"CRITICAL (views_stock_coin): Redis 연결 실패 - {e}.")
        return None
    except Exception as e_init:
        print(f"CRITICAL (views_stock_coin): Redis 클라이언트 초기화 중 오류 - {e_init}.")
        return None


def get_batch_current_prices(request):  # 모든종복 현재가 일괄호출 (보유종목 업뎃에 사용)
    """
    GET 파라미터로 받은 여러 심볼들에 대해 Redis에서 각 심볼의
    1분봉 마지막 closePrice를 조회하여 딕셔너리로 반환합니다.
    호출 예: /api/get_batch_prices/?symbols=TQQQ,BTCUSDT,ETHUSDT
    """
    if request.method != 'GET':
        return JsonResponse({'status': False, 'message': 'GET request required.'}, status=405)

    symbols_param = request.GET.get('symbols', '')
    if not symbols_param:
        return JsonResponse({'status': False, 'message': 'No symbols provided.'}, status=400)

    symbols_list = [s.strip().upper() for s in symbols_param.split(',') if s.strip()]
    if not symbols_list:
        return JsonResponse({'status': False, 'message': 'Symbol list is empty.'}, status=400)

    redis_conn = get_redis_connection_for_kline_view(decode_responses=False)  # 바이트로 받고 직접 디코딩
    if not redis_conn:
        return JsonResponse({'status': False, 'message': 'Redis service unavailable'}, status=503)

    prices_data = {}
    interval_to_fetch = '1m'  # 현재가로는 보통 1분봉 사용

    for symbol in symbols_list:
        redis_key = f"stockdata:{symbol}:{interval_to_fetch}"
        try:
            if not redis_conn.exists(redis_key):
                prices_data[symbol] = None  # 데이터 없음 표시
                print(f"DEBUG [get_batch_prices]: Key '{redis_key}' does not exist in Redis.")
                continue

            key_type = redis_conn.type(redis_key)
            if key_type != b'list':
                prices_data[symbol] = None
                print(
                    f"WARNING [get_batch_prices]: Key '{redis_key}' is not a list (type: {key_type.decode('utf-8')}).")
                continue

            last_kline_json_bytes = redis_conn.lindex(redis_key, -1)
            if last_kline_json_bytes:
                kline_data = json.loads(last_kline_json_bytes.decode('utf-8'))
                close_price = kline_data.get('closePrice')
                if close_price is not None:
                    try:
                        prices_data[symbol] = float(close_price)
                    except ValueError:
                        prices_data[symbol] = None
                        print(
                            f"WARNING [get_batch_prices]: Could not convert closePrice for {symbol} to float: {close_price}")
                else:
                    prices_data[symbol] = None  # closePrice 필드 없음
            else:
                prices_data[symbol] = None  # 리스트는 있지만 비어있음

        except redis.RedisError as r_err:
            print(f"ERROR [get_batch_prices]: Redis error for key '{redis_key}': {r_err}")
            prices_data[symbol] = None  # 오류 시 해당 심볼 가격은 null
        except json.JSONDecodeError as j_err:
            print(f"ERROR [get_batch_prices]: JSON decoding error for key '{redis_key}': {j_err}")
            prices_data[symbol] = None
        except Exception as e:
            print(f"ERROR [get_batch_prices]: Unexpected error for key '{redis_key}': {e}")
            traceback.print_exc()
            prices_data[symbol] = None

    return JsonResponse({'status': True, 'prices': prices_data})










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




