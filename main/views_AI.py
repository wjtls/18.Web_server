
import json
import sys
import os

# 현재 파일의 경로를 기준으로 이전 경로를 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 서브 프로세스 및 랜더
import subprocess
import os
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse

import json
from django.shortcuts import render
from datetime import datetime,timedelta


limit_data_index = 1000

def AI_finance_RAG(request):
    chat_history = []
    try:
        json_file_path = "b_finance_RAG_AI/traj/report_chat_history.json"
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                chat_history.append({
                    'datetime': item.get('datetime', ''),
                    'response': item.get('응답', '')
                })
    except:
        json_file_path = "../b_finance_RAG_AI/traj/report_chat_history.json"
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                chat_history.append({
                    'datetime': item.get('datetime', ''),
                    'response': item.get('응답', '')
                })

    # 날짜순으로 정렬 (오름차순 : 최신 항목이 뒤로 reverse =False)
    chat_history.sort(key=lambda x: datetime.strptime(x['datetime'], "%Y-%m-%d %H:%M:%S"), reverse=True)
    chat_history=chat_history[:5]
    context = {
        'chat_history': chat_history
    }
    return JsonResponse(context)


def AI_trader_1(request):
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



def AI_trader_1_get_data(request):
    # JSON 파일에서 데이터 읽기
    data = []

    # 현재 실행 스크립트의 디렉토리 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 현재 디렉토리에서 상위 디렉토리로 이동한 후 a_FRDdata_api 폴더로 이동
    base_path = os.path.join(current_dir, "..","..", "b_strategy_AI")

    with open(f'{base_path}/2_AI_APPO_LS_stock/traj/backtest_result.json', 'r') as file:
        for line in file:
            data.append(json.loads(line.strip()))

    # DataFrame으로 변환
    df = pd.DataFrame(data)
    # 필요한 데이터 추출
    def extract_data(column_name):
        data = df.loc[df['index'] == column_name, '0'].values[0]['long']

        # 첫 번째 요소가 iterable한지 확인
        res =[item[0] if hasattr(item, '__iter__') and not isinstance(item, str) else item for item in data]
        res = res[-limit_data_index:]
        return res
    pv_data = extract_data('PV_data') #PV 데이터
    pv_return_data = extract_data('PV_return_data') #PV누적수익률
    pv_log_return_data = extract_data('PV_log_return_data') # PV의 로그수익률
    pv_cumul_return_data = extract_data('PV_Cumul_return_data') #PV 로그 누적 수익
    pv_log_cumul_return = extract_data('pv_log_cumul_return') # PV 로그 누적수익을 수익률로 변환(정규화 효과)
    date_data = extract_data('date_data')
    action_data = extract_data('action_data')
    action_ratio =extract_data('buysell_ratio')
    buy_data = extract_data('buy_data')
    sell_data = extract_data('sell_data')
    buy_date = extract_data('buy_date')
    sell_date= extract_data('sell_date')
    price_data = extract_data('price_data')


    monthly_profit_rate = None  # 최근 한달 수익률
    # 계산 로직 구현 예시 (아까 설명한 것과 같음)
    if pv_data and date_data and len(pv_data) == len(date_data) and len(pv_data) > 1:
        try:
            latest_date = datetime.strptime(date_data[-1], '%Y-%m-%d %H:%M:%S')
            date_one_month_ago = latest_date - timedelta(days=30)  # 간단히 30일 전

            start_index = 0
            for i, date_str in enumerate(date_data):
                current_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                if current_date >= date_one_month_ago:
                    start_index = i
                    break  # 한 달 전 날짜보다 같거나 나중인 첫 인덱스 찾으면 중단

            pv_start = pv_data[start_index]  # 한 달 전 시점의 PV
            pv_end = pv_data[-1]  # 최신 PV

            if pv_start is not None and pv_end is not None and pv_start != 0:
                monthly_profit_rate = ((pv_end - pv_start) / pv_start) * 100
                # 소수점 반올림 등 필요하면 여기서 처리 (예: monthly_profit_rate = round(monthly_profit_rate, 2))
            elif pv_start == 0 and pv_end > 0:
                monthly_profit_rate = float('inf')  # 시작이 0이고 끝이 양수면 무한대 수익
            else:
                monthly_profit_rate = None  # 계산 불가능

        except Exception as e:
            print(f"한 달 수익률 계산 오류: {e}")
            monthly_profit_rate = None  # 오류 시 None


    # --- 학습 이후 구간 수익률 계산 로직 추가 ---
    real_trading_profit_rate = None  # 계산된 '학습 이후 구간' 수익률을 저장할 변수
    # 날짜 형식은 date_data의 형식과 일치해야 함
    training_end_date_str = '2024-11-01 00:00:00'
    try:
        # 기준 날짜를 datetime 객체로 변환
        training_end_date = datetime.strptime(training_end_date_str, '%Y-%m-%d %H:%M:%S')  # <- 날짜 형식 맞춰 파싱

        # pv_data와 date_data가 유효하고 데이터가 충분히 있는지 확인
        if pv_data and date_data and len(pv_data) == len(date_data) and len(pv_data) > 1:

            # 1. 학습 종료 기준 날짜에 해당하는 PV 데이터 인덱스 찾기
            #    date_data를 순회하며 training_end_date와 같거나 **나중**인 첫 번째 날짜의 인덱스를 찾음
            #    이 날짜가 '학습 이후 구간'의 시작 시점이 됨.
            start_index_real = -1  # 찾지 못했을 경우 초기값
            for i, date_str in enumerate(date_data):
                try:
                    current_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')  # 날짜 형식 맞춰 파싱
                    if current_date >= training_end_date:
                        start_index_real = i
                        break  # 해당 날짜 이후 데이터의 시작 인덱스 찾으면 중단
                except ValueError:
                    # date_data 중간에 파싱 오류가 있는 경우 건너뛰기
                    print(f"경고: date_data 파싱 오류 발생 ({date_str}). 해당 데이터 건너뜀.")
                    continue  # 다음 데이터로 넘어감

            # 2. 학습 종료 시점 이후의 데이터가 충분히 있는지 확인
            #    (start_index_real을 찾았고, 그 인덱스부터 마지막까지 최소 2개 이상의 데이터가 있어야 수익률 계산 가능)
            if start_index_real != -1 and (len(pv_data) - start_index_real) > 1:
                pv_real_start = pv_data[start_index_real]  # 학습 종료 시점 이후의 첫 PV
                pv_end = pv_data[-1]  # 최신 PV (pv_data의 마지막 값)

                # 3. 수익률 계산
                #    시작 PV가 None이 아니고, 끝 PV가 None이 아니고, 시작 PV가 0이 아닌 경우에만 계산
                if pv_real_start is not None and pv_end is not None and pv_real_start != 0:
                    real_trading_profit_rate = ((pv_end - pv_real_start) / pv_real_start) * 100

                elif pv_real_start == 0 and pv_end > 0:
                    real_trading_profit_rate = float('inf')  # 무한대 또는 특정 문자열 ('Infinity')
                else:
                    real_trading_profit_rate = None  # 또는 0.0, 'N/A' 등으로 설정

            else:
                # 학습 종료 날짜 이후 데이터가 없거나 부족해서 계산 불가
                real_trading_profit_rate = None
                # print(f"Warning: 학습 종료 날짜 ({training_end_date_str}) 이후 데이터가 부족하여 학습 이후 구간 수익률 계산 불가.")


        else:
            real_trading_profit_rate = None

    except ValueError:
        print(
            f"학습 종료 기준 날짜 문자열 ({training_end_date_str}) 또는 date_data 항목의 날짜 형식 오류 발생. 형식을 '%Y-%m-%d %H:%M:%S'와 일치시키세요.")
        real_trading_profit_rate = None

    except Exception as e:
        # 기타 예외 처리
        print(f"학습 이후 구간 수익률 계산 중 예상치 못한 오류 발생: {e}")
        real_trading_profit_rate = None  # 오류 발생 시 수익률 없음으로 처리

    # JSON 형태로 반환
    return JsonResponse({
        'pv': pv_data,
        'pv_return': pv_return_data,
        'pv_log_return_data': pv_log_return_data,
        'pv_cumul_return': pv_cumul_return_data,
        'pv_log_cumul_return': pv_log_cumul_return,
        'date': date_data,
        'buy': buy_data,
        'sell': sell_data,
        'price': price_data,
        'buy_date': buy_date,
        'sell_date': sell_date,
        'action': action_data,
        'action_ratio' :action_ratio,
        'month_profit': monthly_profit_rate,
        'real_profit': real_trading_profit_rate
    })

def AI_trader_2_get_data(request):
    # JSON 파일에서 데이터 읽기
    data = []

    # 현재 실행 스크립트의 디렉토리 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 현재 디렉토리에서 상위 디렉토리로 이동한 후 a_FRDdata_api 폴더로 이동
    base_path = os.path.join(current_dir, "..","..", "b_strategy_AI")

    with open(f'{base_path}/2_AI_APPO_LS_stock_2/traj/backtest_result.json', 'r') as file:
        for line in file:
            data.append(json.loads(line.strip()))

    # DataFrame으로 변환
    df = pd.DataFrame(data)

    # 필요한 데이터 추출
    def extract_data(column_name):
        data = df.loc[df['index'] == column_name, '0'].values[0]['long']

        # 첫 번째 요소가 iterable한지 확인
        res = [item[0] if hasattr(item, '__iter__') and not isinstance(item, str) else item for item in data]
        res = res[-limit_data_index:]
        return res

    pv_data = extract_data('PV_data') #PV 데이터
    pv_return_data = extract_data('PV_return_data') #PV누적수익률
    pv_log_return_data = extract_data('PV_log_return_data') # PV의 로그수익률
    pv_cumul_return_data = extract_data('PV_Cumul_return_data') #PV 로그 누적 수익
    pv_log_cumul_return = extract_data('pv_log_cumul_return') # PV 로그 누적수익을 수익률로 변환(정규화 효과)
    date_data = extract_data('date_data')
    action_data = extract_data('action_data')
    action_ratio =extract_data('buysell_ratio')
    buy_data = extract_data('buy_data')
    sell_data = extract_data('sell_data')
    buy_date = extract_data('buy_date')
    sell_date= extract_data('sell_date')
    price_data = extract_data('price_data')

    monthly_profit_rate = None  # 최근 한달 수익률
    # 계산 로직 구현 예시 (아까 설명한 것과 같음)
    if pv_data and date_data and len(pv_data) == len(date_data) and len(pv_data) > 1:
        try:
            latest_date = datetime.strptime(date_data[-1], '%Y-%m-%d %H:%M:%S')
            date_one_month_ago = latest_date - timedelta(days=30)  # 간단히 30일 전

            start_index = 0
            for i, date_str in enumerate(date_data):
                current_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                if current_date >= date_one_month_ago:
                    start_index = i
                    break  # 한 달 전 날짜보다 같거나 나중인 첫 인덱스 찾으면 중단

            pv_start = pv_data[start_index]  # 한 달 전 시점의 PV
            pv_end = pv_data[-1]  # 최신 PV

            if pv_start is not None and pv_end is not None and pv_start != 0:
                monthly_profit_rate = ((pv_end - pv_start) / pv_start) * 100
                # 소수점 반올림 등 필요하면 여기서 처리 (예: monthly_profit_rate = round(monthly_profit_rate, 2))
            elif pv_start == 0 and pv_end > 0:
                monthly_profit_rate = float('inf')  # 시작이 0이고 끝이 양수면 무한대 수익
            else:
                monthly_profit_rate = None  # 계산 불가능

        except Exception as e:
            print(f"한 달 수익률 계산 오류: {e}")
            monthly_profit_rate = None  # 오류 시 None

    # --- 학습 이후 구간 수익률 계산 로직 추가 ---
    real_trading_profit_rate = None  # 계산된 '학습 이후 구간' 수익률을 저장할 변수
    # 날짜 형식은 date_data의 형식과 일치해야 함
    training_end_date_str = '2025-05-01 00:00:00'
    try:
        # 기준 날짜를 datetime 객체로 변환
        training_end_date = datetime.strptime(training_end_date_str, '%Y-%m-%d %H:%M:%S')  # <- 날짜 형식 맞춰 파싱

        # pv_data와 date_data가 유효하고 데이터가 충분히 있는지 확인
        if pv_data and date_data and len(pv_data) == len(date_data) and len(pv_data) > 1:

            # 1. 학습 종료 기준 날짜에 해당하는 PV 데이터 인덱스 찾기
            #    date_data를 순회하며 training_end_date와 같거나 **나중**인 첫 번째 날짜의 인덱스를 찾음
            #    이 날짜가 '학습 이후 구간'의 시작 시점이 됨.
            start_index_real = -1  # 찾지 못했을 경우 초기값
            for i, date_str in enumerate(date_data):
                try:
                    current_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')  # 날짜 형식 맞춰 파싱
                    if current_date >= training_end_date:
                        start_index_real = i
                        break  # 해당 날짜 이후 데이터의 시작 인덱스 찾으면 중단
                except ValueError:
                    # date_data 중간에 파싱 오류가 있는 경우 건너뛰기
                    print(f"경고: date_data 파싱 오류 발생 ({date_str}). 해당 데이터 건너뜀.")
                    continue  # 다음 데이터로 넘어감

            # 2. 학습 종료 시점 이후의 데이터가 충분히 있는지 확인
            #    (start_index_real을 찾았고, 그 인덱스부터 마지막까지 최소 2개 이상의 데이터가 있어야 수익률 계산 가능)
            if start_index_real != -1 and (len(pv_data) - start_index_real) > 1:
                pv_real_start = pv_data[start_index_real]  # 학습 종료 시점 이후의 첫 PV
                pv_end = pv_data[-1]  # 최신 PV (pv_data의 마지막 값)

                # 3. 수익률 계산
                #    시작 PV가 None이 아니고, 끝 PV가 None이 아니고, 시작 PV가 0이 아닌 경우에만 계산
                if pv_real_start is not None and pv_end is not None and pv_real_start != 0:
                    real_trading_profit_rate = ((pv_end - pv_real_start) / pv_real_start) * 100

                elif pv_real_start == 0 and pv_end > 0:
                    real_trading_profit_rate = float('inf')  # 무한대 또는 특정 문자열 ('Infinity')
                else:
                    real_trading_profit_rate = None  # 또는 0.0, 'N/A' 등으로 설정

            else:
                # 학습 종료 날짜 이후 데이터가 없거나 부족해서 계산 불가
                real_trading_profit_rate = None
                # print(f"Warning: 학습 종료 날짜 ({training_end_date_str}) 이후 데이터가 부족하여 학습 이후 구간 수익률 계산 불가.")


        else:
            real_trading_profit_rate = None

    except ValueError:
        print(
            f"학습 종료 기준 날짜 문자열 ({training_end_date_str}) 또는 date_data 항목의 날짜 형식 오류 발생. 형식을 '%Y-%m-%d %H:%M:%S'와 일치시키세요.")
        real_trading_profit_rate = None

    except Exception as e:
        # 기타 예외 처리
        print(f"학습 이후 구간 수익률 계산 중 예상치 못한 오류 발생: {e}")
        real_trading_profit_rate = None  # 오류 발생 시 수익률 없음으로 처리

    # JSON 형태로 반환
    return JsonResponse({
        'pv': pv_data,
        'pv_return': pv_return_data,
        'pv_log_return_data': pv_log_return_data,
        'pv_cumul_return': pv_cumul_return_data,
        'pv_log_cumul_return': pv_log_cumul_return,
        'date': date_data,
        'buy': buy_data,
        'sell': sell_data,
        'price': price_data,
        'buy_date': buy_date,
        'sell_date': sell_date,
        'action': action_data,
        'action_ratio': action_ratio,
        'month_profit': monthly_profit_rate,
        'real_profit': real_trading_profit_rate
    })

def AI_trader_3_get_data(request):
    # JSON 파일에서 데이터 읽기
    data = []

    # 현재 실행 스크립트의 디렉토리 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 현재 디렉토리에서 상위 디렉토리로 이동한 후 a_FRDdata_api 폴더로 이동
    base_path = os.path.join(current_dir, "..","..", "b_strategy_AI")

    with open(f'{base_path}/2_AI_APPO_LS_stock_TQQQ_61_ver2/traj/backtest_result.json', 'r') as file:
        for line in file:
            data.append(json.loads(line.strip()))

    # DataFrame으로 변환
    df = pd.DataFrame(data)

    # 필요한 데이터 추출
    def extract_data(column_name):
        data = df.loc[df['index'] == column_name, '0'].values[0]['long']

        # 첫 번째 요소가 iterable한지 확인
        res = [item[0] if hasattr(item, '__iter__') and not isinstance(item, str) else item for item in data]
        res = res[-limit_data_index:]
        return res

    pv_data = extract_data('PV_data') #PV 데이터
    pv_return_data = extract_data('PV_return_data') #PV누적수익률
    pv_log_return_data = extract_data('PV_log_return_data') # PV의 로그수익률
    pv_cumul_return_data = extract_data('PV_Cumul_return_data') #PV 로그 누적 수익
    pv_log_cumul_return = extract_data('pv_log_cumul_return') # PV 로그 누적수익을 수익률로 변환(정규화 효과)
    date_data = extract_data('date_data')
    action_data = extract_data('action_data')
    action_ratio =extract_data('buysell_ratio')
    buy_data = extract_data('buy_data')
    sell_data = extract_data('sell_data')
    buy_date = extract_data('buy_date')
    sell_date= extract_data('sell_date')
    price_data = extract_data('price_data')

    monthly_profit_rate = None  # 최근 한달 수익률
    # 계산 로직 구현 예시 (아까 설명한 것과 같음)
    if pv_data and date_data and len(pv_data) == len(date_data) and len(pv_data) > 1:
        try:
            latest_date = datetime.strptime(date_data[-1], '%Y-%m-%d %H:%M:%S')
            date_one_month_ago = latest_date - timedelta(days=30)  # 간단히 30일 전

            start_index = 0
            for i, date_str in enumerate(date_data):
                current_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                if current_date >= date_one_month_ago:
                    start_index = i
                    break  # 한 달 전 날짜보다 같거나 나중인 첫 인덱스 찾으면 중단

            pv_start = pv_data[start_index]  # 한 달 전 시점의 PV
            pv_end = pv_data[-1]  # 최신 PV

            if pv_start is not None and pv_end is not None and pv_start != 0:
                monthly_profit_rate = ((pv_end - pv_start) / pv_start) * 100
                # 소수점 반올림 등 필요하면 여기서 처리 (예: monthly_profit_rate = round(monthly_profit_rate, 2))
            elif pv_start == 0 and pv_end > 0:
                monthly_profit_rate = float('inf')  # 시작이 0이고 끝이 양수면 무한대 수익
            else:
                monthly_profit_rate = None  # 계산 불가능

        except Exception as e:
            print(f"한 달 수익률 계산 오류: {e}")
            monthly_profit_rate = None  # 오류 시 None

    # --- 학습 이후 구간 수익률 계산 로직 추가 ---
    real_trading_profit_rate = None  # 계산된 '학습 이후 구간' 수익률을 저장할 변수
    # 날짜 형식은 date_data의 형식과 일치해야 함
    training_end_date_str = '2025-05-01 00:00:00'
    try:
        # 기준 날짜를 datetime 객체로 변환
        training_end_date = datetime.strptime(training_end_date_str, '%Y-%m-%d %H:%M:%S')  # <- 날짜 형식 맞춰 파싱

        # pv_data와 date_data가 유효하고 데이터가 충분히 있는지 확인
        if pv_data and date_data and len(pv_data) == len(date_data) and len(pv_data) > 1:

            # 1. 학습 종료 기준 날짜에 해당하는 PV 데이터 인덱스 찾기
            #    date_data를 순회하며 training_end_date와 같거나 **나중**인 첫 번째 날짜의 인덱스를 찾음
            #    이 날짜가 '학습 이후 구간'의 시작 시점이 됨.
            start_index_real = -1  # 찾지 못했을 경우 초기값
            for i, date_str in enumerate(date_data):
                try:
                    current_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')  # 날짜 형식 맞춰 파싱
                    if current_date >= training_end_date:
                        start_index_real = i
                        break  # 해당 날짜 이후 데이터의 시작 인덱스 찾으면 중단
                except ValueError:
                    # date_data 중간에 파싱 오류가 있는 경우 건너뛰기
                    print(f"경고: date_data 파싱 오류 발생 ({date_str}). 해당 데이터 건너뜀.")
                    continue  # 다음 데이터로 넘어감

            # 2. 학습 종료 시점 이후의 데이터가 충분히 있는지 확인
            #    (start_index_real을 찾았고, 그 인덱스부터 마지막까지 최소 2개 이상의 데이터가 있어야 수익률 계산 가능)
            if start_index_real != -1 and (len(pv_data) - start_index_real) > 1:
                pv_real_start = pv_data[start_index_real]  # 학습 종료 시점 이후의 첫 PV
                pv_end = pv_data[-1]  # 최신 PV (pv_data의 마지막 값)

                # 3. 수익률 계산
                #    시작 PV가 None이 아니고, 끝 PV가 None이 아니고, 시작 PV가 0이 아닌 경우에만 계산
                if pv_real_start is not None and pv_end is not None and pv_real_start != 0:
                    real_trading_profit_rate = ((pv_end - pv_real_start) / pv_real_start) * 100

                elif pv_real_start == 0 and pv_end > 0:
                    real_trading_profit_rate = float('inf')  # 무한대 또는 특정 문자열 ('Infinity')
                else:
                    real_trading_profit_rate = None  # 또는 0.0, 'N/A' 등으로 설정

            else:
                # 학습 종료 날짜 이후 데이터가 없거나 부족해서 계산 불가
                real_trading_profit_rate = None
                # print(f"Warning: 학습 종료 날짜 ({training_end_date_str}) 이후 데이터가 부족하여 학습 이후 구간 수익률 계산 불가.")


        else:
            real_trading_profit_rate = None

    except ValueError:
        print(
            f"학습 종료 기준 날짜 문자열 ({training_end_date_str}) 또는 date_data 항목의 날짜 형식 오류 발생. 형식을 '%Y-%m-%d %H:%M:%S'와 일치시키세요.")
        real_trading_profit_rate = None

    except Exception as e:
        # 기타 예외 처리
        print(f"학습 이후 구간 수익률 계산 중 예상치 못한 오류 발생: {e}")
        real_trading_profit_rate = None  # 오류 발생 시 수익률 없음으로 처리

    # JSON 형태로 반환
    return JsonResponse({
        'pv': pv_data,
        'pv_return': pv_return_data,
        'pv_log_return_data': pv_log_return_data,
        'pv_cumul_return': pv_cumul_return_data,
        'pv_log_cumul_return': pv_log_cumul_return,
        'date': date_data,
        'buy': buy_data,
        'sell': sell_data,
        'price': price_data,
        'buy_date': buy_date,
        'sell_date': sell_date,
        'action': action_data,
        'action_ratio': action_ratio,
        'month_profit': monthly_profit_rate,
        'real_profit': real_trading_profit_rate
    })

def AI_trader_4_get_data(request):
    # JSON 파일에서 데이터 읽기
    data = []

    # 현재 실행 스크립트의 디렉토리 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 현재 디렉토리에서 상위 디렉토리로 이동한 후 a_FRDdata_api 폴더로 이동
    base_path = os.path.join(current_dir, "..","..", "b_strategy_AI")

    with open(f'{base_path}/2_AI_APPO_LS_stock_AAPU_31/traj/backtest_result.json', 'r') as file:
        for line in file:
            data.append(json.loads(line.strip()))

    # DataFrame으로 변환
    df = pd.DataFrame(data)

    # 필요한 데이터 추출
    def extract_data(column_name):
        data = df.loc[df['index'] == column_name, '0'].values[0]['long']

        # 첫 번째 요소가 iterable한지 확인
        res = [item[0] if hasattr(item, '__iter__') and not isinstance(item, str) else item for item in data]
        res = res[-limit_data_index:]
        return res

    pv_data = extract_data('PV_data') #PV 데이터
    pv_return_data = extract_data('PV_return_data') #PV누적수익률
    pv_log_return_data = extract_data('PV_log_return_data') # PV의 로그수익률
    pv_cumul_return_data = extract_data('PV_Cumul_return_data') #PV 로그 누적 수익
    pv_log_cumul_return = extract_data('pv_log_cumul_return') # PV 로그 누적수익을 수익률로 변환(정규화 효과)
    date_data = extract_data('date_data')
    action_data = extract_data('action_data')
    action_ratio =extract_data('buysell_ratio')
    buy_data = extract_data('buy_data')
    sell_data = extract_data('sell_data')
    buy_date = extract_data('buy_date')
    sell_date= extract_data('sell_date')
    price_data = extract_data('price_data')

    monthly_profit_rate = None  # 최근 한달 수익률
    # 계산 로직 구현 예시 (아까 설명한 것과 같음)
    if pv_data and date_data and len(pv_data) == len(date_data) and len(pv_data) > 1:
        try:
            latest_date = datetime.strptime(date_data[-1], '%Y-%m-%d %H:%M:%S')
            date_one_month_ago = latest_date - timedelta(days=30)  # 간단히 30일 전

            start_index = 0
            for i, date_str in enumerate(date_data):
                current_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                if current_date >= date_one_month_ago:
                    start_index = i
                    break  # 한 달 전 날짜보다 같거나 나중인 첫 인덱스 찾으면 중단

            pv_start = pv_data[start_index]  # 한 달 전 시점의 PV
            pv_end = pv_data[-1]  # 최신 PV

            if pv_start is not None and pv_end is not None and pv_start != 0:
                monthly_profit_rate = ((pv_end - pv_start) / pv_start) * 100
                # 소수점 반올림 등 필요하면 여기서 처리 (예: monthly_profit_rate = round(monthly_profit_rate, 2))
            elif pv_start == 0 and pv_end > 0:
                monthly_profit_rate = float('inf')  # 시작이 0이고 끝이 양수면 무한대 수익
            else:
                monthly_profit_rate = None  # 계산 불가능

        except Exception as e:
            print(f"한 달 수익률 계산 오류: {e}")
            monthly_profit_rate = None  # 오류 시 None

    # --- 학습 이후 구간 수익률 계산 로직 추가 ---
    real_trading_profit_rate = None  # 계산된 '학습 이후 구간' 수익률을 저장할 변수
    # 날짜 형식은 date_data의 형식과 일치해야 함
    training_end_date_str = '2025-05-01 00:00:00'
    try:
        # 기준 날짜를 datetime 객체로 변환
        training_end_date = datetime.strptime(training_end_date_str, '%Y-%m-%d %H:%M:%S')  # <- 날짜 형식 맞춰 파싱

        # pv_data와 date_data가 유효하고 데이터가 충분히 있는지 확인
        if pv_data and date_data and len(pv_data) == len(date_data) and len(pv_data) > 1:

            # 1. 학습 종료 기준 날짜에 해당하는 PV 데이터 인덱스 찾기
            #    date_data를 순회하며 training_end_date와 같거나 **나중**인 첫 번째 날짜의 인덱스를 찾음
            #    이 날짜가 '학습 이후 구간'의 시작 시점이 됨.
            start_index_real = -1  # 찾지 못했을 경우 초기값
            for i, date_str in enumerate(date_data):
                try:
                    current_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')  # 날짜 형식 맞춰 파싱
                    if current_date >= training_end_date:
                        start_index_real = i
                        break  # 해당 날짜 이후 데이터의 시작 인덱스 찾으면 중단
                except ValueError:
                    # date_data 중간에 파싱 오류가 있는 경우 건너뛰기
                    print(f"경고: date_data 파싱 오류 발생 ({date_str}). 해당 데이터 건너뜀.")
                    continue  # 다음 데이터로 넘어감

            # 2. 학습 종료 시점 이후의 데이터가 충분히 있는지 확인
            #    (start_index_real을 찾았고, 그 인덱스부터 마지막까지 최소 2개 이상의 데이터가 있어야 수익률 계산 가능)
            if start_index_real != -1 and (len(pv_data) - start_index_real) > 1:
                pv_real_start = pv_data[start_index_real]  # 학습 종료 시점 이후의 첫 PV
                pv_end = pv_data[-1]  # 최신 PV (pv_data의 마지막 값)

                # 3. 수익률 계산
                #    시작 PV가 None이 아니고, 끝 PV가 None이 아니고, 시작 PV가 0이 아닌 경우에만 계산
                if pv_real_start is not None and pv_end is not None and pv_real_start != 0:
                    real_trading_profit_rate = ((pv_end - pv_real_start) / pv_real_start) * 100

                elif pv_real_start == 0 and pv_end > 0:
                    real_trading_profit_rate = float('inf')  # 무한대 또는 특정 문자열 ('Infinity')
                else:
                    real_trading_profit_rate = None  # 또는 0.0, 'N/A' 등으로 설정

            else:
                # 학습 종료 날짜 이후 데이터가 없거나 부족해서 계산 불가
                real_trading_profit_rate = None
                # print(f"Warning: 학습 종료 날짜 ({training_end_date_str}) 이후 데이터가 부족하여 학습 이후 구간 수익률 계산 불가.")


        else:
            real_trading_profit_rate = None

    except ValueError:
        print(
            f"학습 종료 기준 날짜 문자열 ({training_end_date_str}) 또는 date_data 항목의 날짜 형식 오류 발생. 형식을 '%Y-%m-%d %H:%M:%S'와 일치시키세요.")
        real_trading_profit_rate = None

    except Exception as e:
        # 기타 예외 처리
        print(f"학습 이후 구간 수익률 계산 중 예상치 못한 오류 발생: {e}")
        real_trading_profit_rate = None  # 오류 발생 시 수익률 없음으로 처리

    # JSON 형태로 반환
    return JsonResponse({
        'pv': pv_data,
        'pv_return': pv_return_data,
        'pv_log_return_data': pv_log_return_data,
        'pv_cumul_return': pv_cumul_return_data,
        'pv_log_cumul_return': pv_log_cumul_return,
        'date': date_data,
        'buy': buy_data,
        'sell': sell_data,
        'price': price_data,
        'buy_date': buy_date,
        'sell_date': sell_date,
        'action': action_data,
        'action_ratio': action_ratio,
        'month_profit': monthly_profit_rate,
        'real_profit': real_trading_profit_rate
    })


def AI_trader_5_get_data(request):
    # JSON 파일에서 데이터 읽기
    data = []

    # 현재 실행 스크립트의 디렉토리 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 현재 디렉토리에서 상위 디렉토리로 이동한 후 a_FRDdata_api 폴더로 이동
    base_path = os.path.join(current_dir, "..","..", "b_strategy_AI")

    with open(f'{base_path}/2_AI_APPO_LS_stock_TSLL_61/traj/backtest_result.json', 'r') as file:
        for line in file:
            data.append(json.loads(line.strip()))

    # DataFrame으로 변환
    df = pd.DataFrame(data)

    # 필요한 데이터 추출
    def extract_data(column_name):
        data = df.loc[df['index'] == column_name, '0'].values[0]['long']

        # 첫 번째 요소가 iterable한지 확인
        res = [item[0] if hasattr(item, '__iter__') and not isinstance(item, str) else item for item in data]
        res = res[-limit_data_index:]
        return res

    pv_data = extract_data('PV_data') #PV 데이터
    pv_return_data = extract_data('PV_return_data') #PV누적수익률
    pv_log_return_data = extract_data('PV_log_return_data') # PV의 로그수익률
    pv_cumul_return_data = extract_data('PV_Cumul_return_data') #PV 로그 누적 수익
    pv_log_cumul_return = extract_data('pv_log_cumul_return') # PV 로그 누적수익을 수익률로 변환(정규화 효과)
    date_data = extract_data('date_data')
    action_data = extract_data('action_data')
    action_ratio =extract_data('buysell_ratio')
    buy_data = extract_data('buy_data')
    sell_data = extract_data('sell_data')
    buy_date = extract_data('buy_date')
    sell_date= extract_data('sell_date')
    price_data = extract_data('price_data')

    monthly_profit_rate = None  # 최근 한달 수익률
    # 계산 로직 구현 예시 (아까 설명한 것과 같음)
    if pv_data and date_data and len(pv_data) == len(date_data) and len(pv_data) > 1:
        try:
            latest_date = datetime.strptime(date_data[-1], '%Y-%m-%d %H:%M:%S')
            date_one_month_ago = latest_date - timedelta(days=30)  # 간단히 30일 전

            start_index = 0
            for i, date_str in enumerate(date_data):
                current_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                if current_date >= date_one_month_ago:
                    start_index = i
                    break  # 한 달 전 날짜보다 같거나 나중인 첫 인덱스 찾으면 중단

            pv_start = pv_data[start_index]  # 한 달 전 시점의 PV
            pv_end = pv_data[-1]  # 최신 PV

            if pv_start is not None and pv_end is not None and pv_start != 0:
                monthly_profit_rate = ((pv_end - pv_start) / pv_start) * 100
                # 소수점 반올림 등 필요하면 여기서 처리 (예: monthly_profit_rate = round(monthly_profit_rate, 2))
            elif pv_start == 0 and pv_end > 0:
                monthly_profit_rate = float('inf')  # 시작이 0이고 끝이 양수면 무한대 수익
            else:
                monthly_profit_rate = None  # 계산 불가능

        except Exception as e:
            print(f"한 달 수익률 계산 오류: {e}")
            monthly_profit_rate = None  # 오류 시 None

    # --- 학습 이후 구간 수익률 계산 로직 추가 ---
    real_trading_profit_rate = None  # 계산된 '학습 이후 구간' 수익률을 저장할 변수
    # 날짜 형식은 date_data의 형식과 일치해야 함
    training_end_date_str = '2025-05-01 00:00:00'
    try:
        # 기준 날짜를 datetime 객체로 변환
        training_end_date = datetime.strptime(training_end_date_str, '%Y-%m-%d %H:%M:%S')  # <- 날짜 형식 맞춰 파싱

        # pv_data와 date_data가 유효하고 데이터가 충분히 있는지 확인
        if pv_data and date_data and len(pv_data) == len(date_data) and len(pv_data) > 1:

            # 1. 학습 종료 기준 날짜에 해당하는 PV 데이터 인덱스 찾기
            #    date_data를 순회하며 training_end_date와 같거나 **나중**인 첫 번째 날짜의 인덱스를 찾음
            #    이 날짜가 '학습 이후 구간'의 시작 시점이 됨.
            start_index_real = -1  # 찾지 못했을 경우 초기값
            for i, date_str in enumerate(date_data):
                try:
                    current_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')  # 날짜 형식 맞춰 파싱
                    if current_date >= training_end_date:
                        start_index_real = i
                        break  # 해당 날짜 이후 데이터의 시작 인덱스 찾으면 중단
                except ValueError:
                    # date_data 중간에 파싱 오류가 있는 경우 건너뛰기
                    print(f"경고: date_data 파싱 오류 발생 ({date_str}). 해당 데이터 건너뜀.")
                    continue  # 다음 데이터로 넘어감

            # 2. 학습 종료 시점 이후의 데이터가 충분히 있는지 확인
            #    (start_index_real을 찾았고, 그 인덱스부터 마지막까지 최소 2개 이상의 데이터가 있어야 수익률 계산 가능)
            if start_index_real != -1 and (len(pv_data) - start_index_real) > 1:
                pv_real_start = pv_data[start_index_real]  # 학습 종료 시점 이후의 첫 PV
                pv_end = pv_data[-1]  # 최신 PV (pv_data의 마지막 값)

                # 3. 수익률 계산
                #    시작 PV가 None이 아니고, 끝 PV가 None이 아니고, 시작 PV가 0이 아닌 경우에만 계산
                if pv_real_start is not None and pv_end is not None and pv_real_start != 0:
                    real_trading_profit_rate = ((pv_end - pv_real_start) / pv_real_start) * 100

                elif pv_real_start == 0 and pv_end > 0:
                    real_trading_profit_rate = float('inf')  # 무한대 또는 특정 문자열 ('Infinity')
                else:
                    real_trading_profit_rate = None  # 또는 0.0, 'N/A' 등으로 설정

            else:
                # 학습 종료 날짜 이후 데이터가 없거나 부족해서 계산 불가
                real_trading_profit_rate = None
                # print(f"Warning: 학습 종료 날짜 ({training_end_date_str}) 이후 데이터가 부족하여 학습 이후 구간 수익률 계산 불가.")


        else:
            real_trading_profit_rate = None

    except ValueError:
        print(
            f"학습 종료 기준 날짜 문자열 ({training_end_date_str}) 또는 date_data 항목의 날짜 형식 오류 발생. 형식을 '%Y-%m-%d %H:%M:%S'와 일치시키세요.")
        real_trading_profit_rate = None

    except Exception as e:
        # 기타 예외 처리
        print(f"학습 이후 구간 수익률 계산 중 예상치 못한 오류 발생: {e}")
        real_trading_profit_rate = None  # 오류 발생 시 수익률 없음으로 처리

    # JSON 형태로 반환
    return JsonResponse({
        'pv': pv_data,
        'pv_return': pv_return_data,
        'pv_log_return_data': pv_log_return_data,
        'pv_cumul_return': pv_cumul_return_data,
        'pv_log_cumul_return': pv_log_cumul_return,
        'date': date_data,
        'buy': buy_data,
        'sell': sell_data,
        'price': price_data,
        'buy_date': buy_date,
        'sell_date': sell_date,
        'action': action_data,
        'action_ratio': action_ratio,
        'month_profit': monthly_profit_rate,
        'real_profit': real_trading_profit_rate
    })

def run_backtest(request):  #벡테스트 버튼눌렀을때 작동해야함
    # 백테스트 실행
    script_path = os.path.join('D:\\AI_pycharm\\pythonProject\\3_AI_LLM_finance\\b_strategy_AI\\2_AI_APPO_LS_stock', 'f_back_test.py')
    subprocess.run(['python', script_path], check=True)

    # 결과 파일 읽기
    result_path = os.path.join('D:\\AI_pycharm\\pythonProject\\3_AI_LLM_finance\\b_strategy_AI\\traj', 'result.xlsx')
    results = pd.read_csv(result_path)

    # 결과를 딕셔너리로 변환
    result_dict = results.to_dict(orient='records')

    return render(request, 'result.html', {'results': result_dict})






