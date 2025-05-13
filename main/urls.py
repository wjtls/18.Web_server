
from django.urls import path, include
from django.contrib import admin

from django.views.generic import RedirectView #배포

from . import views_korea_stock
from . import views_main
from . import views_stock_coin
from . import views_AI

# Django 내장 LoginView와 LogoutView 임포트
from django.contrib.auth import views as auth_views
'''
예시
path("list/", views_korea_stock.korea_stock_list, name="korea_stock_list") 에서

1. list/는 웹에서 오는 요청임 (타 사이트 api이용하는경우 이는 고정돼있음)
2. views_korea_stock.korea_stock_list 요청이 오면 실행하는 함수
3. HTML에서 사용
   table id = list 로 사용해야함
   <a href="{% url 'korea_stock_list' %}">국내 주식 목록</a> 로 사용가능
'''

urlpatterns = [
    #웹 요소들
    path('profile/settings/', views_main.profile_settings_view, name='profile_settings'), #유저프로필 설정시 호출
    path('api/trade/process_result/', views_main.process_trade_result_api_view, name='process_trade_result_api'), # 이전 단계에서 추가한 API
    path('api/shop/purchase/', views_main.purchase_item_api_view, name='purchase_item_api'),       # 상점 API
    path('api/wallet/withdraw/', views_main.initiate_withdrawal_api_view, name='initiate_withdrawal_api'), # 출금 API 경로 추가
    path('api/get_websocket_key/', views_main.get_websocket_key_api, name='get_websocket_key_api'),#웹소켓 api호출,
    path('api/update_portfolio/', views_main.update_portfolio_api, name='update_portfolio_api'), #포폴 DB에 업데이트
    path('api/load_portfolio/', views_main.load_portfolio_api, name='load_portfolio_api'), #포폴 DB에서 로드
    path('accounts/profile/', views_main.profile, name='profile'),
    path('base/', auth_views.LoginView.as_view(template_name='main/base'), name='base'),
    path('setup_2fa/', auth_views.LoginView.as_view(template_name='main/setup_2fa'), name='setup_2fa'),
    path('dashboard/', auth_views.LoginView.as_view(template_name='main/dashboard.html'), name='dashboard'),
    path('register/', views_main.register_view, name='register'),
    path('logout/', auth_views.LogoutView.as_view(template_name='main/logout.html'), name='logout'),
    path('login/',auth_views.LoginView.as_view(template_name='main/login.html'),name='login'),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),

    # 게시판 URL 추가 (예: '/board/' 경로 사용)
    path('board/', include('board.urls')), # board 앱의 urls.py 연결

    #데이터
    path('api/realtime_candle/<str:market>/<str:interval>/<str:symbol>/', views_stock_coin.get_realtime_candle_data, name='realtime_candle'),
    path("oversea_news/", views_stock_coin.oversea_news, name="oversea_stock_ask"),
    path("oversea_api/<str:minute>/<str:symbol>/<str:exchange_code>", views_stock_coin.load_stock_coin_data, name="oversea_stock_ask"), #가격(해외주식, 코인 통합)
    path("oversea_past_api/<str:minute>/<str:symbol>/<str:data_number>/", views_stock_coin.oversea_past_api, name="oversea_past_stock_ask"), #과거 시뮬레이션용 데이터

    # 코인 데이터
    path("coin_list/", views_stock_coin.coin_list, name="coin_list"),
    # 해외주식 데이터
    path("oversea_list/", views_stock_coin.oversea_stock_list, name="oversea_stock_list"),
    path("oversea_NASD_list/", views_stock_coin.oversea_NASD_stock_list, name="oversea_stock_NASD_list"),
    path("oversea_NYSE_list/", views_stock_coin.oversea_NYSE_stock_list, name="oversea_stock_NYSE_list"),
    path("oversea_AMEX_list/", views_stock_coin.oversea_AMEX_stock_list, name="oversea_stock_AMEX_list"),

    #페이지
    path("", views_main.index, name="index"),
    path("main", views_main.chat_return, name="main"),
    path("index2", views_main.index2_simulator, name="index2_simulator"),
    path("index2_1", views_main.index2_1, name="index2_1_past_simulator"),
    path("index3", views_main.index3_strategy, name="index3_strategy"),
    path("index4", views_main.index4_user_market, name="index4_user_market"),
    path("marketing_page", views_main.marketing_page, name="marketing_page"),


    #AI
    path('run_backtest/', views_AI.run_backtest, name='run_backtest'),
    path('api/trader1/data/', views_AI.AI_trader_1_get_data, name='ai_trader_1_data'),
    path('api/trader2/data/', views_AI.AI_trader_2_get_data, name='ai_trader_2_data'),
    path('api/trader3/data/', views_AI.AI_trader_3_get_data, name='ai_trader_3_data'),
    path('api/trader4/data/', views_AI.AI_trader_4_get_data, name='ai_trader_4_data'),
    path('run_fin_RAG/', views_AI.AI_finance_RAG, name='ai_fin_rag'),

]

# 배포
from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])