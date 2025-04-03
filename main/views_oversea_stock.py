
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



# Create your views here.


def oversea_api(request, minute, symbol, exchange_code):
    # 한투API 실시간 호출
    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M")
    data_count = ["2010-01-01 00:00", now]
    ACCESS_TOKEN , token_time= get_ovsstk_chart_price.get_access_token()
    print(ACCESS_TOKEN, 'access token')

    # 실시간 데이터 호출
    real_time_data = get_ovsstk_chart_price.fetch_and_save_data(exchange_code, symbol, 1, 40, ACCESS_TOKEN) #거래소코드,심볼

    # 현재 실행 스크립트의 디렉토리 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 현재 디렉토리에서 상위 디렉토리로 이동한 후 a_FRDdata_api 폴더로 이동
    base_path = os.path.join(current_dir, "..","..", "a_FRDdata_api")

    # 파일 이름
    file_name_pattern = f"{symbol}_full_1min_adjsplitdiv.txt"

    # glob을 사용하여 해당 경로에 있는 모든파일에서 찾음
    print(f'찾으려는 경로,파일 명 : {base_path}/{file_name_pattern}')
    search_pattern = os.path.join(base_path, '**', file_name_pattern)
    files = glob.glob(search_pattern, recursive=True)

    if files:
        past_data_name = files[0]  # 첫 번째로 찾은 파일 사용
        past_data = pd.read_csv(past_data_name)
        past_data.columns = ['datetime', 'open', 'high', 'low', 'last', 'evol']
        print(f"FRD 데이터 파일 서치완료: {past_data_name}")
    else:
        print(f"저장된 FRD 데이터 전체에서 파일을 찾을 수 없습니다.   찾은 파일 : {past_data_name}")
        past_data_name = files  # 첫 번째로 찾은 파일 사용
        past_data =pd.read_csv(past_data_name)


    # 형식 변환
    past_data['datetime'] = pd.to_datetime(past_data['datetime'])
    real_time_data['datetime'] = pd.to_datetime(real_time_data['datetime'])

    # 분봉 변환

    # datetime 열을 인덱스로 설정
    past_data.set_index('datetime', inplace=True)
    real_time_data.set_index('datetime', inplace=True)

    # 시간 필터
    past_data = past_data.between_time('09:00', '16:00')
    real_time_data = real_time_data.between_time('09:00', '16:00')

    print(past_data,'이전 데이터', minute, '설정 분봉', symbol, '심볼')
    print(real_time_data, '실시간 데이터', minute, '설정 분봉', symbol, '심볼')
    # 합침
    combined_data = pd.concat([past_data, real_time_data], axis=0)
    combined_data.reset_index(inplace=True)
    combined_data = combined_data.drop_duplicates(subset='datetime')
    combined_data.columns = ['Datetime', 'open', 'high', 'low', 'last','volume', 'eamt']

    # datetime 형식으로 변환
    start_date = pd.to_datetime(data_count[0])
    end_date = pd.to_datetime(data_count[1])

    # 최종 데이터 추출
    filtered_data = combined_data[
        (combined_data['Datetime'] >= start_date) & (combined_data['Datetime'] <= end_date)]

    df = filtered_data[['Datetime', 'open', 'high', 'low', 'last', 'volume']]
    data_set = pd.DataFrame(df).reset_index()
    #data_set = total_time_Frame(data_set.values.tolist(), minute, data_set.columns)

    # 각 열을 Series로 변환 및 NaN 처리
    open_ = pd.to_numeric(data_set['open'], errors='coerce').fillna(0).astype(float).tolist()
    close_ = pd.to_numeric(data_set['last'], errors='coerce').fillna(0).astype(float).tolist()
    high_ = pd.to_numeric(data_set['high'], errors='coerce').fillna(0).astype(float).tolist()
    low_ = pd.to_numeric(data_set['low'], errors='coerce').fillna(0).astype(float).tolist()
    vol = pd.to_numeric(data_set['volume'], errors='coerce').fillna(0).astype(float).tolist()
    date = pd.to_datetime(data_set['Datetime'])  # Datetime 형식으로 변환

    # 데이터프레임을 사용하여 데이터 생성
    data = {
        'x': date,
        'o': open_,
        'h': high_,
        'l': low_,
        'c': close_
    }

    # 각 열을 리스트로 변환
    data_list = []
    for i in range(len(data['x'])):
        data_list.append({
            'localDate': pd.to_datetime(data['x'].iloc[i]),  # ISO 형식으로 변환
            'openPrice': float(data['o'][i]),
            'highPrice': float(data['h'][i]),
            'lowPrice': float(data['l'][i]),  #
            'closePrice': float(data['c'][i])  #
        })
    data_list =data_list[-10000:]
    print('데이터 개수 :',len(data_list))
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




