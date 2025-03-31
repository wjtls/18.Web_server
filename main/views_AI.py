
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
from datetime import datetime


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
        return [item[0] if hasattr(item, '__iter__') and not isinstance(item, str) else item for item in data]

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
        'action_ratio' :action_ratio
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






