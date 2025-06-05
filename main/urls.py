
from django.urls import path, include
from django.contrib import admin

from django.views.generic import RedirectView #배포

from . import views_korea_stock
from . import views_main
from . import views_stock_coin
from . import views_AI
from . import views_app
from . import views_blockchain

from payments import views as payment_views

# Django 내장 LoginView와 LogoutView 임포트
from django.contrib.auth import views as auth_views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView, # 선택 사항
)


from django.contrib import admin
from django.urls import path, include # include를 import 했는지 확인!



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
    path('account/delete/', views_main.account_delete_view, name='account_delete'),
    path('api/trade/process_result/', views_main.process_trade_result_api_view, name='process_trade_result_api'), # 이전 단계에서 추가한 API
    path('api/shop/purchase/', payment_views.purchase_item_api_view, name='purchase_item_api'),       # 상점 API
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
    path('api/realtime_candle/<str:market>/<str:interval>/<str:symbol>/', views_stock_coin.get_realtime_candle_data, name='realtime_candle'), #심볼에 해당하는 현재가 조회
    path('api/get_batch_prices/', views_stock_coin.get_batch_current_prices, name='get_batch_current_prices_api'),#모든 종목 현재가 일괄 조회

    path("oversea_news/", views_stock_coin.oversea_news, name="oversea_stock_ask"),         #뉴스
    path("oversea_api/<str:minute>/<str:symbol>/<str:exchange_code>/", views_stock_coin.load_stock_coin_data, name="oversea_stock_ask"), #가격(해외주식, 코인 통합)
    path("oversea_ask_api/<str:data_type_or_interval>/<str:symbol>/<str:exchange_code>/", views_stock_coin.load_stock_coin_ASK_data, name="oversea_stock_ask_data"), #호가(해외주식, 코인 통합)
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
    path("index5", views_main.index5_community, name="index5_community"),
    path("marketing/", views_main.marketing_page, name="marketing_page"),

    # 카드등록 페이지
    path('payment/', include('payments.urls')),
    path('payment/add-card/', payment_views.add_card_view, name='add_card'),
    path('payment/card-registration-success/', payment_views.card_registration_success_view,
         name='card_registration_success'),


    #AI
    path('run_backtest/', views_AI.run_backtest, name='run_backtest'),
    path('api/trader1/data/', views_AI.AI_trader_1_get_data, name='ai_trader_1_data'),
    path('api/trader2/data/', views_AI.AI_trader_2_get_data, name='ai_trader_2_data'),
    path('api/trader3/data/', views_AI.AI_trader_3_get_data, name='ai_trader_3_data'),
    path('api/trader4/data/', views_AI.AI_trader_4_get_data, name='ai_trader_4_data'),
    path('api/trader5/data/', views_AI.AI_trader_5_get_data, name='ai_trader_5_data'),
    path('run_fin_RAG/', views_AI.AI_finance_RAG, name='ai_fin_rag'),

    #시스템 (코인차감등)
    path('api/trigger_coin_deduction/', views_main.trigger_coin_deduction_api, name='trigger_coin_deduction_api'),

    #소셜 로그인, 회원가입
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),


    # 회원가입 2차인증,닉네임,휴대폰인증 AJAX URLS
    path('ajax/check_username/', views_main.check_username_view, name='check_username'),
    path('ajax/check_nickname/', views_main.check_nickname_view, name='check_nickname'),
    path('ajax/send_otp/', views_main.send_otp_view, name='send_otp'),
    path('ajax/verify_otp/', views_main.verify_otp_view, name='verify_otp'),






    ###################################################### 앱 전용 API URL
    path('api/trade/process_result/app/', views_app.AppTradeProcessAPI.as_view(), name='process_trade_result_api'),
    path('api/get-csrf-token/', views_main.get_csrf_token_api, name='get_csrf_token_api'),  # 토큰 가져오기
    #path('api/app/login/', views_app.app_login_api, name='app_login_api'),  #로그인
    path('api/app/register/', views_app.app_register_api, name='app_register_api'), # 회원가입
    path('api/load_portfolio/app/', views_app.app_load_portfolio_api, name='load_portfolio_api'),  # 포폴 DB에서 로드
    path('api/platform-quiz/', views_app.load_platform_quiz_data, name='load_platform_quiz_data'), #퀴즈데이터 호출

    # 앱 전용 인증 API (JWT 사용)
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # 로그인 (토큰 발급)
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # 토큰 갱신
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'), # 토큰 유효성 검사 (선택)

    #래퍼럴
    path('api/v1/referrals/', include('referrals.urls', namespace='referrals_api')),

    #코인가치, 상점
    path('api/asi-coin/value/', views_blockchain.get_asi_coin_value, name='api_get_asi_coin_value'),
    path('api/shop/purchase-item/', views_blockchain.PurchaseItemAPI.as_view(), name='api_purchase_item'),
    path('api/shop/subscribe-plan/', views_blockchain.SubscribePlanAPI.as_view(), name='api_subscribe_plan'),
    path('activate-title/', views_blockchain.ActivateTitleAPI.as_view(), name='activate_title'),
]

# 배포
from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])