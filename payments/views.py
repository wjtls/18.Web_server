# payments/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.http import JsonResponse  # AJAX 응답이 필요하다면 (현재는 폼 제출 후 리디렉션)
from django.urls import reverse

from django.contrib.auth import get_user_model




from payments.models import PaymentLog
from main.models import Title, UserOwnedTitle


User = get_user_model()

from .models import UserPaymentMethod, Subscription

import requests  # 아임포트 API 호출을 위해 (pip install requests 필요)
import time  # merchant_uid 생성 등
import json  # request.body 파싱 (만약 JS에서 JSON으로 보낸다면)

N_DAYS_FREE_TRIAL = getattr(settings, 'N_DAYS_FREE_TRIAL', 3)


@login_required
def add_card_view(request):
    iamport_store_id = getattr(settings, 'IAMPORT_STORE_ID', None)
    iamport_api_key = getattr(settings, 'IAMPORT_API_KEY', None)
    iamport_api_secret = getattr(settings, 'IAMPORT_API_SECRET', None)

    if not iamport_store_id or not iamport_api_key or not iamport_api_secret:
        messages.error(request, _("결제 시스템 설정(아임포트)이 올바르지 않습니다. 관리자에게 문의해주세요."))
        # 네임스페이스를 사용하지 않는다면 'index'
        return redirect(
            'index' if not hasattr(settings, 'PAYMENTS_APP_NAME') else f"{settings.PAYMENTS_APP_NAME}:index")

    if request.method == 'POST':
        user = request.user
        imp_uid = request.POST.get('imp_uid')
        merchant_uid_from_client = request.POST.get('merchant_uid')
        # customer_uid는 JS에서 IMP.request_pay 호출 시 사용했던 값을 그대로 받아야 함
        customer_uid_from_client = request.POST.get('customer_uid')

        print(
            f"[ADD_CARD_VIEW - IAMPORT] POST 데이터: imp_uid={imp_uid}, merchant_uid={merchant_uid_from_client}, customer_uid={customer_uid_from_client}")

        if not imp_uid or not merchant_uid_from_client or not customer_uid_from_client:
            messages.error(request, _("카드 인증 정보가 올바르게 전달되지 않았습니다. 다시 시도해주세요."))
            # 네임스페이스를 사용하지 않는다면 'add_card'
            return redirect('payments:add_card' if hasattr(settings, 'PAYMENTS_APP_NAME') else 'add_card')

        access_token = None
        try:
            # 1. 아임포트 API 액세스 토큰 발급
            token_url = "https://api.iamport.kr/users/getToken"
            token_payload = {
                'imp_key': iamport_api_key,
                'imp_secret': iamport_api_secret
            }
            print("[ADD_CARD_VIEW - IAMPORT] 아임포트 토큰 발급 요청...")
            token_res = requests.post(token_url, data=token_payload, timeout=10)
            token_res.raise_for_status()  # 오류 시 HTTPError 발생
            token_data = token_res.json()
            if token_data.get('code') != 0 or not token_data.get('response', {}).get('access_token'):
                raise ValueError(f"아임포트 토큰 발급 실패: {token_data.get('message', '알 수 없는 오류')}")
            access_token = token_data['response']['access_token']
            print(f"[ADD_CARD_VIEW - IAMPORT] 아임포트 토큰 발급 성공")

        except requests.exceptions.RequestException as e:
            print(f"[ADD_CARD_VIEW - IAMPORT] 아임포트 토큰 발급 API 네트워크 오류: {e}")
            messages.error(request, _("결제 서버 접속에 실패했습니다. 잠시 후 다시 시도해주세요. (토큰)"))
            return redirect('payments:add_card')
        except (KeyError, ValueError) as e:
            print(f"[ADD_CARD_VIEW - IAMPORT] 아임포트 토큰 응답 처리 오류: {e}")
            messages.error(request, _("결제 서버 응답 처리에 실패했습니다. (토큰)"))
            return redirect('payments:add_card')
        except Exception as e:
            print(f"[ADD_CARD_VIEW - IAMPORT] 아임포트 토큰 발급 중 알 수 없는 오류: {e}")
            messages.error(request, _("결제 시스템 오류입니다. (토큰)"))
            return redirect('payments:add_card')

        if access_token and imp_uid:
            try:
                # 2. 아임포트 API로 결제(카드 인증) 정보 조회 및 검증
                payment_info_url = f"https://api.iamport.kr/payments/{imp_uid}"
                headers = {'Authorization': f'Bearer {access_token}'}
                print(f"[ADD_CARD_VIEW - IAMPORT] 아임포트 결제 정보 ({imp_uid}) 조회 요청...")
                payment_res = requests.get(payment_info_url, headers=headers, timeout=10)
                payment_res.raise_for_status()
                payment_data = payment_res.json()['response']

                print(
                    f"[ADD_CARD_VIEW - IAMPORT] 결제 정보: 상태={payment_data.get('status')}, 금액={payment_data.get('amount')}, 주문ID={payment_data.get('merchant_uid')}, 고객ID={payment_data.get('customer_uid')}")

                # === 검증 로직 ===
                # 카드 등록(빌링키 발급)을 위한 인증 결제 금액 (JavaScript에서 설정한 amount와 일치해야 함)
                expected_auth_amount = Decimal('100.00')  # 예시: 100원 (JS와 동일해야 함)

                if payment_data.get('status') == 'paid' and \
                        Decimal(str(payment_data.get('amount'))) == expected_auth_amount and \
                        payment_data.get('merchant_uid') == merchant_uid_from_client and \
                        payment_data.get('customer_uid') == customer_uid_from_client:

                    print(f"[ADD_CARD_VIEW - IAMPORT] 카드 인증 결제 검증 성공!")

                    with transaction.atomic():
                        # UserPaymentMethod 정보 저장 또는 업데이트
                        card_name_from_pg = payment_data.get('card_name', '카드 정보 없음')
                        # 아임포트에서 카드번호 일부는 card_number 필드로 제공될 수 있음 (마스킹되어)
                        # 또는 pg_provider, emb_pg_provider 등으로 PG사 정보도 확인 가능
                        card_last4_from_pg = payment_data.get('card_number', '')
                        if card_last4_from_pg and len(card_last4_from_pg) > 4:  # 보통 끝 4자리 또는 앞 6자리 + 끝 4자리
                            card_last4_from_pg = card_last4_from_pg[-4:]
                        elif not card_last4_from_pg:
                            card_last4_from_pg = "XXXX"

                        payment_method_obj, created = UserPaymentMethod.objects.update_or_create(
                            user=user,
                            defaults={
                                'pg_customer_id': customer_uid_from_client,  # 아임포트 customer_uid가 빌링키 역할
                                'pg_payment_method_id': imp_uid,  # 이번 인증 거래의 imp_uid
                                'card_brand': card_name_from_pg,
                                'last4': card_last4_from_pg,
                                'is_default': True
                            }
                        )
                        print(f"[ADD_CARD_VIEW - IAMPORT] UserPaymentMethod 저장/업데이트: {payment_method_obj}")

                        # 사용자 구독 플랜 "N일 무료이용"으로 변경
                        user.subscription_plan = 'N_DAY_FREE_TRIAL'
                        trial_end_date = timezone.now() + timedelta(days=N_DAYS_FREE_TRIAL)
                        user.current_subscription_end_date = trial_end_date
                        user.save(update_fields=['subscription_plan', 'current_subscription_end_date'])

                        Subscription.objects.update_or_create(
                            user=user,
                            defaults={
                                'plan_name': 'N_DAY_FREE_TRIAL',
                                'start_date': timezone.now(),
                                'end_date': trial_end_date,
                                'status': 'trialing',
                                'auto_renew': True,
                                'pg_customer_id': customer_uid_from_client
                            }
                        )
                        print(f"[ADD_CARD_VIEW - IAMPORT] 사용자 {user.username} 플랜 'N일 무료체험'으로 변경, 만료: {trial_end_date}")
                        messages.success(request, _(f"{N_DAYS_FREE_TRIAL}일 무료 체험이 시작되었습니다! AI 트레이더 페이지를 이용해보세요."))
                        return redirect('payments:card_registration_success')  # 네임스페이스 사용 시
                else:
                    print(f"[ADD_CARD_VIEW - IAMPORT] !!! 카드 인증 결제 검증 실패 !!!")
                    print(
                        f"    PG 상태: {payment_data.get('status')}, PG 금액: {payment_data.get('amount')}, 예상 금액: {expected_auth_amount}")
                    print(f"    PG 주문ID: {payment_data.get('merchant_uid')}, 클라이언트 주문ID: {merchant_uid_from_client}")
                    print(f"    PG 고객ID: {payment_data.get('customer_uid')}, 클라이언트 고객ID: {customer_uid_from_client}")
                    messages.error(request, _("카드 인증 정보 검증에 실패했습니다. 다시 시도해주세요."))
                    # TODO: 필요한 경우 아임포트 결제 취소 API 호출 (이미 결제된 금액이 있다면)
                    # (보통 카드 등록 인증용 소액 결제는 자동 취소되거나, PG사 설정에 따름)

            except requests.exceptions.RequestException as e:
                print(f"[ADD_CARD_VIEW - IAMPORT] 아임포트 결제 정보 조회 API 네트워크 오류: {e}")
                messages.error(request, _("결제 정보 확인 중 오류가 발생했습니다."))
            except (KeyError, ValueError) as e:  # JSON 파싱 또는 필수 키 부재
                print(f"[ADD_CARD_VIEW - IAMPORT] 아임포트 결제 정보 응답 처리 오류: {e}")
                messages.error(request, _("결제 정보 응답 처리에 실패했습니다."))
            except Exception as e:
                print(f"[ADD_CARD_VIEW - IAMPORT] !!! 카드 등록 DB 처리 중 일반 예외: {e} !!!")
                import traceback
                traceback.print_exc()
                messages.error(request, _("카드 등록 처리 중 예상치 못한 오류가 발생했습니다."))
        else:  # 토큰 발급 실패 시 (위에서 이미 메시지 처리 및 리디렉션 되어야 함)
            pass  # messages.error(request, _("결제 서버 인증에 실패했습니다."))

        # 어떤 이유로든 성공적으로 redirect되지 못했다면 (예: 토큰 발급 실패 후), 다시 카드 등록 페이지로
        # (주의: `stripe_publishable_key` 대신 `iamport_store_id`를 전달해야 하지만, 현재 템플릿은 stripe_publishable_key를 기대하고 있음. 템플릿 JS도 수정 필요)
        # 이 부분은 GET 요청으로 리디렉션하는 것이 더 깔끔합니다.
        return redirect('payments:add_card')

    # GET 요청 시
    context = {
        'iamport_store_id': iamport_store_id,  # 템플릿 JS에서 IMP.init()에 사용
        'user_info': {  # IMP.request_pay()에 전달할 사용자 정보 (선택 사항)
            'name': request.user.nickname or request.user.username,
            'email': request.user.email or "",
            'phone': request.user.phone_number or ""
        },
        'merchant_uid': f"regcard_{request.user.id}_{int(time.time())}",  # 빌링키 발급용 고유 주문번호
        'N_DAYS_FREE_TRIAL': N_DAYS_FREE_TRIAL
    }
    return render(request, 'payments/card_add_page.html', context)


@login_required
def card_registration_success_view(request):
    # 간단한 성공 안내 페이지
    return render(request, 'payments/card_registration_success.html')


# payments/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime  # datetime 추가
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse, NoReverseMatch  # NoReverseMatch 추가

from django.contrib.auth import get_user_model

User = get_user_model()

from .models import UserPaymentMethod, Subscription, PaymentLog  # PaymentLog도 추가 가정

import requests  # 아임포트 API 호출 위해
import time  # merchant_uid 생성 등
import json
from decimal import Decimal  # Decimal 사용 위해

# --- 설정값 (settings.py 또는 이 파일 상단에 정의) ---
N_DAYS_FREE_TRIAL = getattr(settings, 'N_DAYS_FREE_TRIAL', 3)

# --- 실제 플랜 및 아이템 가격 정보 (보안을 위해 반드시 서버에 정의!) ---
PLANS_CONFIG = {
    'basic': {'name_kr': '베이직 월간', 'amount': Decimal('3900'), 'currency': 'KRW',
              'stripe_price_id_placeholder': 'price_xxxx_basic'},
    'standard': {'name_kr': '스탠다드 월간', 'amount': Decimal('6900'), 'currency': 'KRW',
                 'stripe_price_id_placeholder': 'price_xxxx_standard'},
    'premium': {'name_kr': '프리미엄 월간', 'amount': Decimal('19900'), 'currency': 'KRW',
                'stripe_price_id_placeholder': 'price_xxxx_premium'},
}

SHOP_ITEMS_CASH_CONFIG = {
    'cash_refill': {'name_kr': '모의투자 머니 초기화', 'amount': Decimal('10000.0'), 'currency': 'KRW'},
    'asi_refill': {'name_kr': 'ASI 코인 충전', 'amount_per_unit': Decimal('1000.0'), 'currency': 'KRW',
                   'is_quantity_based': True},
    'wl_reset': {'name_kr': '승패 초기화', 'amount': Decimal('4000.0'), 'currency': 'KRW'},
    'nickname_color': {'name_kr': '닉네임 색상 변경권', 'amount': Decimal('1000.0'), 'currency': 'KRW'},
    'level_xp_1000': {'name_kr': '레벨 경험치 +1000', 'amount': Decimal('100.0'), 'currency': 'KRW'},
    'profile_cosmetic': {'name_kr': '프로필 꾸미기', 'amount': Decimal('5000.0'), 'currency': 'KRW'},
    'view_trader': {'name_kr': '트레이더 포지션 (1주일)', 'amount': Decimal('100000.0'), 'currency': 'KRW'},
    'strategy_page_sub': {'name_kr': 'AI 트레이더 구독 (1주일)', 'amount': Decimal('100000.0'), 'currency': 'KRW'},
    'auto_trade_10h': {'name_kr': '자동매매 시간 (10시간)', 'amount': Decimal('1000.0'), 'currency': 'KRW'},
    'strategy_sub_profit': {'name_kr': '전략 구독 (수익률 비례)', 'is_dynamic_price': True, 'currency': 'KRW',
                            'rate_per_percent': Decimal('1000.0')},
}


# --- 아임포트 API 통신을 위한 헬퍼 함수 ---
def get_iamport_access_token():
    token_url = "https://api.iamport.kr/users/getToken"
    token_payload = {
        'imp_key': settings.IAMPORT_API_KEY,
        'imp_secret': settings.IAMPORT_API_SECRET
    }
    try:
        token_res = requests.post(token_url, data=token_payload, timeout=10)
        token_res.raise_for_status()
        token_data = token_res.json()
        if token_data.get('code') == 0 and token_data.get('response', {}).get('access_token'):
            print("[IAMPORT_TOKEN] 토큰 발급 성공")
            return token_data['response']['access_token']
        else:
            print(f"[IAMPORT_TOKEN_ERROR] 토큰 발급 실패 응답: {token_data.get('message')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"[IAMPORT_TOKEN_ERROR] API 요청 실패: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"[IAMPORT_TOKEN_ERROR] 응답 JSON 처리 실패: {e}")
        return None


# --- 카드 등록 뷰 (add_card_view)는 이전 답변에 이미 전체 코드가 있습니다. ---
# (add_card_view 함수는 여기에 그대로 있어야 합니다.)
@login_required
def add_card_view(request):
    # ... (이전 답변에서 제공한 add_card_view 함수 전체 내용) ...
    # (주의: 이 함수 내에서도 IAMPORT_API_KEY, IAMPORT_API_SECRET, N_DAYS_FREE_TRIAL 사용)
    # (주의: 이 함수 내에서도 Subscription, UserPaymentMethod 모델 사용)
    iamport_store_id = getattr(settings, 'IAMPORT_STORE_ID', None)
    iamport_api_key = getattr(settings, 'IAMPORT_API_KEY', None)
    iamport_api_secret = getattr(settings, 'IAMPORT_API_SECRET', None)

    if not iamport_store_id or not iamport_api_key or not iamport_api_secret:
        messages.error(request, _("결제 시스템 설정(아임포트)이 올바르지 않습니다. 관리자에게 문의해주세요."))
        return redirect(
            'index' if not hasattr(settings, 'PAYMENTS_APP_NAME') else f"{settings.PAYMENTS_APP_NAME}:index")

    if request.method == 'POST':
        user = request.user
        imp_uid = request.POST.get('imp_uid')
        merchant_uid_from_client = request.POST.get('merchant_uid')
        customer_uid_from_client = request.POST.get('customer_uid')

        print(
            f"[ADD_CARD_VIEW - IAMPORT] POST 데이터: imp_uid={imp_uid}, merchant_uid={merchant_uid_from_client}, customer_uid={customer_uid_from_client}")

        if not imp_uid or not merchant_uid_from_client or not customer_uid_from_client:
            messages.error(request, _("카드 인증 정보가 올바르게 전달되지 않았습니다. 다시 시도해주세요."))
            return redirect('payments:add_card')

        access_token = get_iamport_access_token()  # 헬퍼 함수 사용
        if not access_token:
            messages.error(request, _("결제 서버 인증에 실패했습니다. (토큰)"))
            return redirect('payments:add_card')

        # ... (이하 add_card_view의 POST 로직 - 이전 답변 참고하여 아임포트 결제 검증 및 DB 저장) ...
        # try: ... except ... 블록 포함
        # 이 부분은 이전 답변의 add_card_view POST 로직을 여기에 그대로 넣어주세요.
        # 핵심: 아임포트 결제내역 상세조회 API 호출 -> 검증 -> UserPaymentMethod, User, Subscription 업데이트
        # 임시로 성공 처리 (실제 연동 필요)
        try:
            with transaction.atomic():
                payment_method_obj, created = UserPaymentMethod.objects.update_or_create(
                    user=user,
                    defaults={
                        'pg_customer_id': customer_uid_from_client,
                        'pg_payment_method_id': imp_uid,
                        'card_brand': "TestCard",  # 실제로는 아임포트 응답에서
                        'last4': "0000",  # 실제로는 아임포트 응답에서
                        'is_default': True
                    }
                )
                user.subscription_plan = 'N_DAY_FREE_TRIAL'
                trial_end_date = timezone.now() + timedelta(days=N_DAYS_FREE_TRIAL)
                user.current_subscription_end_date = trial_end_date
                user.save(update_fields=['subscription_plan', 'current_subscription_end_date'])

                Subscription.objects.update_or_create(
                    user=user,
                    defaults={
                        'plan_name': 'N_DAY_FREE_TRIAL',
                        'start_date': timezone.now(),
                        'end_date': trial_end_date,
                        'status': 'trialing', 'auto_renew': True,
                        'pg_customer_id': customer_uid_from_client
                    }
                )
                messages.success(request, _(f"{N_DAYS_FREE_TRIAL}일 무료 체험이 시작되었습니다!"))
                return redirect('payments:card_registration_success')
        except Exception as e:
            messages.error(request, _(f"카드 등록 처리 중 오류: {e}"))
            return redirect('payments:add_card')

    # GET 요청 시
    context = {
        'iamport_store_id': iamport_store_id,
        'user_info': {
            'name': request.user.nickname or request.user.username,
            'email': request.user.email or "",
            'phone': request.user.phone_number or ""
        },
        'merchant_uid': f"regcard_{request.user.id}_{int(time.time())}",
        'N_DAYS_FREE_TRIAL': N_DAYS_FREE_TRIAL
    }
    return render(request, 'payments/card_add_page.html', context)


@login_required
def card_registration_success_view(request):
    return render(request, 'payments/card_registration_success.html')


# --- ▼▼▼ 여기에 create_subscription_view 함수 추가 ▼▼▼ ---
@login_required
@require_POST
def create_subscription_view(request):
    user = request.user
    access_token = get_iamport_access_token()
    if not access_token:
        return JsonResponse({'success': False, 'message': _('결제 서버 인증에 실패했습니다. (토큰)')}, status=500)

    try:
        data = json.loads(request.body)
        plan_id_from_client = data.get('plan_id')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': _('잘못된 요청 형식입니다.')}, status=400)

    plan_info = PLANS_CONFIG.get(plan_id_from_client)
    if not plan_info:
        return JsonResponse({'success': False, 'message': _('유효하지 않은 플랜입니다.')}, status=400)

    try:
        payment_method = UserPaymentMethod.objects.get(user=user, is_default=True)
        if not payment_method.pg_customer_id:
            return JsonResponse(
                {'success': False, 'message': _('등록된 결제 카드 정보(빌링키)가 없습니다.'), 'needs_card_registration': True,
                 'add_card_url': reverse('payments:add_card')})
    except UserPaymentMethod.DoesNotExist:
        return JsonResponse(
            {'success': False, 'message': _('등록된 카드가 없습니다. 먼저 카드를 등록해주세요.'), 'needs_card_registration': True,
             'add_card_url': reverse('payments:add_card')})

    merchant_uid_for_sub = f"sub_{plan_id_from_client}_{user.id}_{int(time.time())}"
    payload = {
        'customer_uid': payment_method.pg_customer_id,
        'merchant_uid': merchant_uid_for_sub,
        'amount': plan_info['amount'],
        'name': plan_info['name_kr'],
        'buyer_name': user.nickname or user.username,
        'buyer_email': user.email,
        'buyer_tel': user.phone_number or "",
        # 아임포트 정기결제 관련 파라미터는 문서를 참고하여 추가해야 합니다.
        # 예: 'recurring': True, 'pg': 'stripe' (아임포트 대시보드 Stripe 채널 연동 시)
        # 현재는 단건 결제 API (/subscribe/payments/again) 사용을 가정합니다.
    }
    print(f"[CREATE_SUBSCRIPTION] 아임포트 결제 요청 데이터: {payload}")

    try:
        payment_again_url = "https://api.iamport.kr/subscribe/payments/again"
        headers = {'Authorization': f'Bearer {access_token}'}
        res = requests.post(payment_again_url, headers=headers, json=payload, timeout=10)
        res.raise_for_status()  # 4xx, 5xx 응답 시 예외 발생
        payment_result = res.json()

        if payment_result.get('code') == 0 and payment_result.get('response') and payment_result['response'].get(
                'status') == 'paid':
            pg_response = payment_result['response']
            print(f"[CREATE_SUBSCRIPTION] 아임포트 결제 성공: imp_uid={pg_response.get('imp_uid')}")

            with transaction.atomic():
                sub_end_date = timezone.now() + timedelta(days=30)  # 예시: 1개월 구독
                subscription, created = Subscription.objects.update_or_create(
                    user=user,
                    defaults={
                        'plan_name': plan_id_from_client.upper(),  # 'BASIC', 'STANDARD', 'PREMIUM'
                        'start_date': timezone.now(),
                        'end_date': sub_end_date,
                        'status': 'active',  # 결제 성공 시 'active'
                        'auto_renew': True,  # 정기결제라면 True
                        'pg_customer_id': payment_method.pg_customer_id,
                        'pg_subscription_id': pg_response.get('imp_uid')  # 또는 PG사에서 받은 실제 구독 ID
                    }
                )
                user.subscription_plan = plan_id_from_client.upper()
                user.current_subscription_end_date = sub_end_date
                user.save(update_fields=['subscription_plan', 'current_subscription_end_date'])

                PaymentLog.objects.create(
                    user=user, subscription=subscription, amount=plan_info['amount'],
                    currency=plan_info.get('currency', 'KRW'),
                    pg_transaction_id=pg_response.get('imp_uid'),
                    status='succeeded',
                    description=f"{plan_info['name_kr']} 구독 (카드)"
                )
            # messages.success(request, _(f"'{plan_info['name_kr']}' 구독이 시작되었습니다!")) # AJAX 응답이므로 messages 대신 JSON
            return JsonResponse(
                {'success': True, 'message': _('구독이 성공적으로 시작되었습니다!'), 'redirect_url': reverse('index3_strategy')})
        else:
            error_msg_from_pg = payment_result.get('message', _('알 수 없는 결제 오류'))
            print(f"[CREATE_SUBSCRIPTION] 아임포트 결제 실패: {error_msg_from_pg}")
            return JsonResponse({'success': False, 'message': f"결제 실패: {error_msg_from_pg}"})

    except requests.exceptions.HTTPError as http_err:
        error_content_msg = "서버 응답 오류"
        try:
            error_content_msg = http_err.response.json().get('message', str(http_err))
        except:
            pass
        print(
            f"[CREATE_SUBSCRIPTION] 아임포트 API HTTP 오류: {http_err.response.text if http_err.response else str(http_err)}")
        return JsonResponse({'success': False, 'message': f"결제 요청 중 오류(HTTP): {error_content_msg}"},
                            status=http_err.response.status_code if http_err.response else 500)
    except requests.exceptions.RequestException as req_err:
        print(f"[CREATE_SUBSCRIPTION] 아임포트 API 네트워크 오류: {req_err}")
        return JsonResponse({'success': False, 'message': _('결제 요청 중 네트워크 오류가 발생했습니다.')}, status=503)
    except Exception as e:
        print(f"[CREATE_SUBSCRIPTION] !!! 구독 처리 중 일반 예외 발생: {e} !!!")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': _('구독 처리 중 서버 내부 오류가 발생했습니다.')}, status=500)


# --- ▼▼▼ 여기에 charge_item_card_view 함수 추가 ▼▼▼ ---
@login_required
@require_POST
def charge_item_card_view(request):
    user = request.user
    access_token = get_iamport_access_token()
    if not access_token:
        return JsonResponse({'success': False, 'message': _('결제 서버 인증에 실패했습니다. (토큰)')}, status=500)

    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1)) if item_id == 'asi_refill' else 1  # ASI 충전만 수량 고려
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'success': False, 'message': _('잘못된 요청 형식입니다.')}, status=400)

    item_info = SHOP_ITEMS_CASH_CONFIG.get(item_id)
    if not item_info:
        return JsonResponse({'success': False, 'message': _('유효하지 않은 아이템입니다.')}, status=400)

    actual_amount_to_charge = Decimal('0.0')
    item_name_for_payment = item_info['name_kr']

    if item_info.get('is_quantity_based'):  # 예: asi_refill
        if quantity <= 0: return JsonResponse({'success': False, 'message': _('수량은 1 이상이어야 합니다.')}, status=400)
        actual_amount_to_charge = item_info['amount_per_unit'] * quantity
        item_name_for_payment += f" x{quantity}"
    elif item_info.get('is_dynamic_price'):
        return JsonResponse({'success': False, 'message': _('동적 가격 아이템은 이 API로 처리할 수 없습니다.')}, status=400)
    elif 'amount' in item_info:
        actual_amount_to_charge = item_info['amount']
    else:
        return JsonResponse({'success': False, 'message': _('아이템 가격 정보가 없습니다.')}, status=400)

    if actual_amount_to_charge <= 0:
        return JsonResponse({'success': False, 'message': _('결제할 금액이 없습니다. (0원 결제 불가)')}, status=400)

    try:
        payment_method = UserPaymentMethod.objects.get(user=user, is_default=True)
        if not payment_method.pg_customer_id:
            return JsonResponse(
                {'success': False, 'message': _('등록된 결제 카드 정보(빌링키)가 없습니다.'), 'needs_card_registration': True,
                 'add_card_url': reverse('payments:add_card')})
    except UserPaymentMethod.DoesNotExist:
        return JsonResponse(
            {'success': False, 'message': _('등록된 카드가 없습니다. 먼저 카드를 등록해주세요.'), 'needs_card_registration': True,
             'add_card_url': reverse('payments:add_card')})

    merchant_uid_for_item = f"item_{item_id}_{user.id}_{int(time.time())}"
    payload = {
        'customer_uid': payment_method.pg_customer_id,
        'merchant_uid': merchant_uid_for_item,
        'amount': actual_amount_to_charge,
        'name': item_name_for_payment,
        'buyer_name': user.nickname or user.username,
        'buyer_email': user.email,
        'buyer_tel': user.phone_number or "",
    }
    print(f"[CHARGE_ITEM_CARD] 아임포트 결제 요청 데이터: {payload}")

    try:
        payment_again_url = "https://api.iamport.kr/subscribe/payments/again"
        headers = {'Authorization': f'Bearer {access_token}'}
        res = requests.post(payment_again_url, headers=headers, json=payload, timeout=10)
        res.raise_for_status()
        payment_result = res.json()

        if payment_result.get('code') == 0 and payment_result.get('response') and payment_result['response'].get(
                'status') == 'paid':
            pg_response = payment_result['response']
            print(f"[CHARGE_ITEM_CARD] 아이템 카드 결제 성공: imp_uid={pg_response.get('imp_uid')}")

            with transaction.atomic():
                user_reloaded = User.objects.select_for_update().get(pk=user.pk)
                item_effect_message = f"'{item_name_for_payment}' 구매가 완료되었습니다."

                # 아이템 효과 적용
                if item_id == 'cash_refill':
                    user_reloaded.cash = F('cash') + 1000000.0  # 또는 고정값으로 덮어쓰기
                    user_reloaded.save(update_fields=['cash'])
                    item_effect_message = "모의투자 머니가 1,000,000 $ 초기화(또는 추가)되었습니다."
                elif item_id == 'asi_refill':
                    user_reloaded.asi_coin_balance = F('asi_coin_balance') + Decimal(str(quantity))
                    user_reloaded.save(update_fields=['asi_coin_balance'])
                    item_effect_message = f"ASI 코인 {quantity}개가 충전되었습니다."
                elif item_id == 'wl_reset':
                    user_reloaded.total_wins = 0
                    user_reloaded.total_losses = 0
                    user_reloaded.save(update_fields=['total_wins', 'total_losses'])
                    item_effect_message = "승패 기록이 초기화되었습니다."
                # ... (다른 아이템 ID에 대한 효과 적용 로직 추가) ...

                user_reloaded.refresh_from_db()

                PaymentLog.objects.create(
                    user=user_reloaded, amount=actual_amount_to_charge,
                    currency=item_info.get('currency', 'KRW'),
                    pg_transaction_id=pg_response.get('imp_uid'),
                    status='succeeded', description=f"{item_name_for_payment} 구매 (카드)"
                )

            # messages.success(request, item_effect_message) # AJAX 응답이므로 messages 대신 JSON
            return JsonResponse({
                'success': True, 'message': item_effect_message,
                'new_asi_balance_str': str(user_reloaded.asi_coin_balance.quantize(Decimal("0.0001"))),
                # JS에서 숫자 변환 용이하도록 문자열
                'new_real_cash_str': str(user_reloaded.real_cash),  # 실제 현금은 이 거래로 변동 없음 (PG사가 처리)
                'new_sim_cash_str': str(user_reloaded.cash)  # 모의투자 현금
            })
        else:
            error_msg_from_pg = payment_result.get('message', _('알 수 없는 결제 오류'))
            print(f"[CHARGE_ITEM_CARD] 아이템 카드 결제 실패: {error_msg_from_pg}")
            return JsonResponse({'success': False, 'message': f"아이템 결제 실패: {error_msg_from_pg}"})

    except Exception as e:  # ... (일반 오류 처리, 이전과 유사) ...
        print(f"[CHARGE_ITEM_CARD] !!! 아이템 카드 결제 처리 중 일반 예외 발생: {e} !!!")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': _('아이템 결제 처리 중 서버 내부 오류가 발생했습니다.')}, status=500)









from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse, NoReverseMatch

# --- User 모델을 올바르게 가져옵니다 ---
from django.contrib.auth import get_user_model # Django의 권장 방식
User = get_user_model()

# --- payments 앱의 모델들을 가져옵니다 ---
from .models import UserPaymentMethod, Subscription, PaymentLog

import requests
import time

###############아이템구매

from django.http import JsonResponse
from django.views.decorators.http import require_POST # POST 요청만 받도록
from django.views.decorators.csrf import csrf_exempt # 필요시 CSRF 예외 처리 (JS에서 토큰 보내는것 권장)
from django.contrib.auth.decorators import login_required # 로그인 필수
import json
from django.utils import timezone
from datetime import timedelta

from chart.blockchain_reward import spend_asi_coin # 사용자가 chart 폴더 언급했으므로 임시 적용
from main.models import StrategyPageSubscription, PositionViewSubscription




# view_main.py

# ... 필요한 import (json, Decimal, transaction, User 등) ...
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.db.models import F
import traceback

# User 모델 import (네 models.py에 정의된 User 모델 정확히 import)
from django.contrib.auth import get_user_model
User = get_user_model()
# --------------------------------------------------------------------









# TODO: spend_asi_coin 함수가 User 모델 메서드로 구현되어 있어야 함
# 이 함수는 user 객체 (락 걸린), 차감할 Decimal 금액, 아이템 이름 받음.
# asi_coin_balance 필드가 DecimalField여야 정확하며, 실제 ASI 출금 연동 로직이 포함되어야 함.
# 성공 시 True, 잔액 부족 또는 오류 시 False 반환.
# 예시 (User 모델 메서드로 정의되어 있다고 가정):
# def spend_asi_coin(self, amount: Decimal, item_name=""): ...


# TODO: Real Cash 가격 1 ASI = 1000 KRW (고정 환율 가정)
# 실제 환경에서는 이 가격이 변동될 수 있으며, 별도 시스템에서 관리/계산되어야 함.
# 이 상수는 view_main.py 파일의 맨 위나 설정 파일에 정의되어 있어야 함.
ASI_KRW_RATE = Decimal("1000.0")


@login_required
@require_POST
@csrf_exempt # JavaScript에서 CSRF 토큰을 헤더에 포함하여 보내는 경우 이 줄은 주석 처리하거나 삭제
def purchase_item_api_view(request):
    """
    ASI Coin 상점 아이템 구매 요청을 처리하고, 결제 방식에 따라
    real_cash, 모의투자 현금, 또는 ASI 코인을 차감하며 아이템 효과를 적용하는 API 뷰.
    가격은 백엔드에 하드코딩된 값을 사용합니다.
    """
    print("\n[DEBUG] ===== purchase_item_api_view 시작 =====")
    try:
        # 1. 요청 본문에서 JSON 데이터 파싱
        data = json.loads(request.body)
        item_id = data.get('item_id') # 구매할 아이템의 ID (프론트엔드에서 받음)
        payment_method = data.get('payment_method') # 결제 방식 ('asi', 'cash', 'sim_cash') (프론트엔드에서 받음)
        purchase_quantity = data.get('quantity') # ASI 코인 충전 등 수량 (프론트엔드에서 받음)
        selected_color = data.get('color') # 닉네임 색상 변경 시 (프론트엔드에서 받음)
        target_user_id = data.get('target_user_id') # 트레이더 포지션 보기 등 (프론트엔드에서 받음)
        strategy_id = data.get('strategy_id') # 전략 구독 시 (프론트엔드에서 받음)
        profit_ratio = data.get('profit_ratio') # 수익률 비례 결제 시 수익률 (프론트엔드에서 받음)

        user = request.user # 요청을 보낸 로그인된 사용자
        user_id = user.id

        #  칭호 구매를 위한 데이터 받기 ▼▼▼ ---
        item_type = data.get('item_type')  # 'title' 또는 일반 아이템의 경우 None/생략됨
        chosen_color = data.get('chosen_color') if item_type == 'title' else None

        print(f"로그: 사용자 {user.username} 아이템 구매 요청 수신 - Item ID: {item_id}, 결제 방식: {payment_method}")
        print(f"로그: 수량: {purchase_quantity}, 색상: {selected_color}, 대상ID: {target_user_id}, 전략ID: {strategy_id}, 수익률: {profit_ratio}")


        # 2. 아이템 정보 및 백엔드 가격 정의 (★★★ 보안 핵심: 가격은 여기에 정의!) ★★★
        # price는 Decimal 타입으로 정확하게 정의.
        # cost_type: 'cash' (real_cash 차감), 'asi' (asi_coin_balance 차감), 'sim_cash' (user.cash 차감)
        items_info = {
            'cash_refill': {'cost_type': 'cash', 'price': Decimal("10000.0"), 'name': "모의투자 머니 초기화"},
            'cash_refill': {'cost_type': 'asi', 'price': Decimal("1.0"), 'name': "모의투자 머니 초기화"},
            'level_xp_1000': {'cost_type': 'cash', 'price': Decimal("100.0"), 'name': "레벨 경험치 +1000"},
            'wl_reset': {'cost_type': 'cash', 'price': Decimal("4000.0"), 'name': "승패 초기화"},
            'nickname_color': {'cost_type': 'cash', 'price': Decimal("1000.0"), 'name': "닉네임 색상 변경권"},
            'profile_cosmetic': {'cost_type': 'cash', 'price': Decimal("5000.0"), 'name': "프로필 꾸미기"}, # 예시 가격
            # ASI 코인 충전: 가격은 수량*1000원, 현금 결제. price는 None으로 정의하고 로직에서 계산.
            'asi_refill': {'cost_type': 'cash', 'price': None, 'name': "ASI 코인 충전"},
            # 칭호 구매: 모의투자 현금 결제, 레벨 제한. price는 모의투자 현금 가격.
            'title_purchase': {'cost_type': 'sim_cash', 'price': Decimal("1000000.0"), 'name': "칭호 구매", 'level_required': 5},
            # ASI 코인 결제 아이템들 (현금 결제 옵션도 있으면 cost_type/price 쌍 추가)
            'view_trader': {'cost_type': 'asi', 'price': Decimal("100.0"), 'name': "트레이더 포지션 보기 (1주일)"}, # 현금 결제 옵션 추가 가능
            'strategy_page_sub': {'cost_type': 'asi', 'price': Decimal("100.0"), 'name': "AI 트레이더 구독 (1주일)"}, # 현금 결제 옵션 추가 가능
            'auto_trade_10h': {'cost_type': 'asi', 'price': Decimal("1.0"), 'name': "자동매매 시간 충전 (10시간)"}, # 현금 결제 옵션 추가 가능
            # 수익률 비례 결제: 가격은 동적 계산, 결제 방식은 프론트에서 지정
            'strategy_sub_profit': {'cost_type': 'dynamic', 'name': "전략 구독 (수익률 비례)", 'asi_rate_per_percent': Decimal("1.0"), 'cash_rate_per_percent': ASI_KRW_RATE}, # 수익률 1%당 1 ASI, 1%당 1000원
        }

        # 3. 요청된 item_id 유효성 확인 및 기본 정보 가져오기
        if item_id not in items_info:
             print(f"오류: 사용자 {user.username} - 알 수 없는 아이템 ID 수신: {item_id}")
             return JsonResponse({'success': False, 'message': '알 수 없는 아이템입니다.'}, status=400)

        item_info = items_info[item_id]
        item_name = item_info['name']
        backend_cost_type_definition = item_info.get('cost_type') # 백엔드에 정의된 결제 타입 (dynamic일 수 있음)
        backend_fixed_price = item_info.get('price')         # 백엔드에 정의된 고정 가격 (None일 수 있음)


        # --- 4. 결제 방식 및 아이템 ID에 따른 실제 차감 금액 결정 및 차감 시도 ---
        amount_to_deduct = Decimal("0.0") # 실제로 차감될 금액
        actual_cost_type_used = None     # 실제로 어떤 잔액에서 차감했는지 기록
        deduction_success = False        # 차감 성공 여부

        # DB 업데이트 및 차감은 원자적 트랜잭션으로 묶음
        try:
            with transaction.atomic():
                # 사용자 객체 최신 상태 로드 및 락 설정 (DB에서 데이터를 가져옴)
                user_locked = User.objects.select_for_update().get(pk=user_id)

                # === 아이템 ID 및 결제 방식에 따른 가격 결정 및 차감 로직 ===

                # --- ASI 코인 충전 (asi_refill) ---
                if item_id == 'asi_refill':
                    if payment_method != 'cash':
                         raise ValueError(f"'{item_name}' 아이템은 현금으로만 구매 가능합니다.")
                    if purchase_quantity is None or not isinstance(purchase_quantity, int) or purchase_quantity <= 0:
                         raise ValueError("올바른 코인 충전 수량(정수, 1 이상)이 필요합니다.")

                    amount_to_deduct = Decimal(str(purchase_quantity)) * ASI_KRW_RATE # KRW 가격 계산
                    actual_cost_type_used = 'cash' # 실제 차감은 현금

                    # 현금 차감 시도 (User 모델 메서드 사용)
                    if not user_locked.spend_real_cash(amount_to_deduct):
                         raise ValueError("현금 잔액이 부족하거나 결제 중 오류가 발생했습니다.")

                    # 차감 성공 시, 사용자 ASI 코인 잔액 증가
                    user_locked.asi_coin_balance += Decimal(str(purchase_quantity))
                    user_locked.save(update_fields=['asi_coin_balance']) # ASI 잔액 변경사항 저장
                    deduction_success = True
                    result_message = f"ASI 코인 {purchase_quantity}개가 충전되었습니다!"

                # --- ▼▼▼ [추가] 칭호 구매 로직 (item_type == 'title' 인 경우) ▼▼▼ ---
                if item_id == 'title':
                    print(f"[PURCHASE_API] 칭호 구매 처리 시작: {item_id}")
                    try:
                        title_obj = Title.objects.get(title_id=item_id, is_purchasable=True)
                        item_name = title_obj.name  # 로그 및 메시지용 이름
                    except Title.DoesNotExist:
                        raise ValueError(f"구매할 수 없거나 존재하지 않는 칭호입니다: '{item_id}'")

                    # 1. 구매 조건 확인 (예: 레벨)
                    # Title 모델의 purchase_conditions JSON 필드 또는 required_level 필드 사용
                    required_level_from_title = 0
                    if title_obj.purchase_conditions and 'level_required' in title_obj.purchase_conditions:
                        required_level_from_title = title_obj.purchase_conditions.get('level_required', 0)
                    elif hasattr(title_obj, 'required_level'):  # 모델에 필드가 직접 있다면
                        required_level_from_title = title_obj.required_level

                    if user_locked.current_level < required_level_from_title:
                        raise ValueError(
                            f"'{title_obj.name}' 칭호는 레벨 {required_level_from_title} 이상부터 구매 가능합니다. (현재 레벨: {user_locked.current_level})")

                    # 2. 색상 유효성 검사
                    if not title_obj.is_color_selectable:
                        chosen_color = title_obj.default_display_color
                    elif not chosen_color or not re.match(r'^#[0-9a-fA-F]{6}$', chosen_color, re.IGNORECASE):
                        print(
                            f"경고: 칭호 '{title_obj.name}' 구매 시 잘못된 색상 코드({chosen_color})로 기본색({title_obj.default_display_color}) 사용")
                        chosen_color = title_obj.default_display_color

                    # 3. 가격 결정 및 차감
                    if payment_method == 'asi' and title_obj.price_asi is not None:
                        amount_to_deduct = title_obj.price_asi
                        if not user_locked.spend_asi_coin(amount_to_deduct, f"칭호 구매: {title_obj.name}"):
                            raise ValueError("ASI 코인 잔액이 부족합니다.")
                    elif payment_method == 'cash' and title_obj.price_cash is not None:
                        amount_to_deduct = title_obj.price_cash
                        # 중요! 실제 현금(카드) 결제는 여기서 아임포트 빌링키 결제 API를 호출해야 합니다.
                        # 지금은 User.real_cash를 사용하는 시뮬레이션입니다.
                        # 실제 구현 시: charge_item_card_view 와 유사한 PG사 연동 로직 필요
                        print(
                            f"경고: '{title_obj.name}' 칭호 현금 결제({amount_to_deduct}원)는 User.real_cash에서 직접 차감됩니다. (실제 PG 연동 필요)")
                        if not user_locked.spend_real_cash(amount_to_deduct):
                            raise ValueError("보유 현금이 부족합니다. (실제 카드 결제 실패 시 이 메시지)")
                    elif payment_method == 'sim_cash' and title_obj.price_sim_cash is not None:
                        amount_to_deduct = title_obj.price_sim_cash
                        if not user_locked.spend_sim_cash(amount_to_deduct):
                            raise ValueError("모의투자 현금이 부족합니다.")
                    else:
                        raise ValueError(f"'{title_obj.name}' 칭호에 대한 유효한 결제 수단('{payment_method}') 또는 가격 정보가 없습니다.")

                    deduction_success = True

                    # 4. UserOwnedTitle 생성 또는 업데이트
                    owned_title, created = UserOwnedTitle.objects.update_or_create(
                        user=user_locked,
                        title=title_obj,
                        defaults={'chosen_color': chosen_color, 'purchased_at': timezone.now()}
                    )
                    if created:
                        result_message = _("'{title_name}' 칭호를 획득했습니다! (색상: {color})").format(
                            title_name=title_obj.name, color=chosen_color)
                    else:
                        result_message = _("'{title_name}' 칭호의 색상을 '{color}'(으)로 변경했습니다. (이미 보유)").format(
                            title_name=title_obj.name, color=chosen_color)

                    action_success = True  # 칭호 획득/색상변경 성공

                    # (선택) 칭호 구매 시 바로 대표 칭호로 설정
                    # user_locked.active_title_text = title_obj.name
                    # user_locked.active_title_color = chosen_color
                    # user_locked.save(update_fields=['active_title_text', 'active_title_color'])

                # --- 칭호 구매 (title_purchase) ---
                elif item_id == 'title_purchase':
                    if payment_method != 'sim_cash':
                        raise ValueError(f"'{item_name}' 아이템은 모의투자 현금으로만 구매 가능합니다.")
                    # 레벨 제한 확인 (User 모델의 @property 사용)
                    level_required = item_info.get('level_required', 0)
                    if user_locked.current_level < level_required:
                         raise ValueError(f"레벨 {level_required} 이상만 구매 가능합니다. (현재 레벨: {user_locked.current_level})")

                    amount_to_deduct = backend_fixed_price # 모의투자 현금 가격
                    actual_cost_type_used = 'sim_cash' # 실제 차감은 모의 현금

                    # 모의 현금 차감 시도 (User 모델 메서드 사용)
                    if not user_locked.spend_sim_cash(amount_to_deduct):
                         raise ValueError("모의투자 현금이 부족하거나 구매 중 오류가 발생했습니다.")

                    # TODO: 사용자에게 칭호 부여 로직 구현 (UserTitle 모델 등)
                    # UserTitle.objects.create(user=user_locked, title='구매한칭호') # 예시

                    deduction_success = True
                    result_message = f"'{item_name}' 칭호를 획득했습니다!"


                # --- 전략 구독 (수익률 비례) (strategy_sub_profit) ---
                elif item_id == 'strategy_sub_profit':
                     # 복잡한 로직: 가격 계산 -> 차감 -> 구독 활성화
                     # 프론트에서 전략 ID와 수익률 정보를 받아야 함.
                     if not strategy_id: raise ValueError("구독할 전략 ID가 필요합니다.")
                     if profit_ratio is None or not isinstance(profit_ratio, (int, float)): raise ValueError("유효한 수익률 정보가 필요합니다.")

                     profit_ratio_decimal = Decimal(str(profit_ratio)) # Decimal로 변환

                     # TODO: 백엔드에서 해당 전략의 실제 수익률 다시 검증하는 로직 추가 권장
                     # actual_strategy_profit_ratio = get_strategy_profit(strategy_id) # 백엔드 함수 가정
                     # if abs(profit_ratio_decimal - actual_strategy_profit_ratio) > Decimal("0.01"): # 허용 오차 설정
                     #     raise ValueError("전략 수익률 정보가 일치하지 않습니다. 다시 시도해주세요.")

                     # 가격 계산 (수익률 1%당 1 ASI 또는 1000원)
                     asi_rate_per_percent = item_info.get('asi_rate_per_percent', Decimal("0"))
                     cash_rate_per_percent = item_info.get('cash_rate_per_percent', Decimal("0"))


                     if payment_method == 'asi':
                          # 가격 in ASI = 수익률(소수점) * 100 * ASI_rate_per_percent
                          amount_to_deduct = profit_ratio_decimal * Decimal("100.0") * asi_rate_per_percent # ASI 단위 계산
                          actual_cost_type_used = 'asi'
                          # ASI 코인 차감 시도
                          if not user_locked.spend_asi_coin(amount_to_deduct, item_name):
                              raise ValueError("ASI 코인 잔액이 부족합니다.")
                          # TODO: 실제 출금 트랜잭션 해시 기록/조회 로직 추가
                          # tx_hash = ...

                     elif payment_method == 'cash':
                          # 가격 in KRW = 수익률(소수점) * 100 * cash_rate_per_percent
                          amount_to_deduct = profit_ratio_decimal * Decimal("100.0") * cash_rate_per_percent # KRW 단위 계산
                          actual_cost_type_used = 'cash'
                           # 현금 차감 시도
                          if not user_locked.spend_real_cash(amount_to_deduct):
                              raise ValueError("현금 잔액이 부족합니다.")
                     else:
                         raise ValueError("알 수 없는 결제 방식입니다.")

                     # TODO: 전략 구독 활성화 로직 구현 (StrategySubscription 모델 등)
                     # StrategySubscription.objects.create(subscriber=user_locked, strategy_id=strategy_id, end_date=timezone.now() + timedelta(days=7)) # 예시

                     deduction_success = True
                     result_message = f"'{item_name}' 구독 완료! ({amount_to_deduct:.2f} {'ASI' if payment_method == 'asi' else 'KRW'} 차감)" # 메시지 동적 표시


                # --- 그 외 모든 표준 아이템 (고정 가격, cash 또는 asi 결제) ---
                else: # item_id가 위 특별 케이스가 아닌 경우
                     if backend_cost_type_definition is None or backend_fixed_price is None:
                          raise ValueError(f"'{item_name}' 아이템의 가격 정보가 불완전합니다.")

                     # 요청된 결제 방식이 백엔드에 정의된 타입과 일치하는지 확인
                     if payment_method != backend_cost_type_definition:
                         raise ValueError(f"'{item_name}' 아이템은 '{backend_cost_type_definition}' 결제만 지원합니다.")


                     amount_to_deduct = backend_fixed_price # 백엔드에 정의된 고정 가격 사용
                     actual_cost_type_used = backend_cost_type_definition # 사용된 결제 타입

                     if actual_cost_type_used == 'cash':
                         # 현금 차감 시도 (User 모델 메서드 사용)
                         if not user_locked.spend_real_cash(amount_to_deduct):
                             raise ValueError("현금 잔액이 부족합니다.")
                         deduction_success = True
                         result_message = f"'{item_name}' 구매 완료! ({amount_to_deduct:.0f} KRW 차감)" # 원화는 소수점 없앰

                     elif actual_cost_type_used == 'asi':
                         # ASI 코인 차감 시도 (User 모델 메서드 사용)
                         if not user_locked.spend_asi_coin(amount_to_deduct, item_name):
                              raise ValueError("ASI 코인 잔액이 부족합니다.")
                         deduction_success = True
                         result_message = f"'{item_name}' 구매 완료! ({amount_to_deduct:.4f} ASI 차감)" # ASI는 소수점 표시
                         # TODO: ASI 출금 시 tx_hash 기록/조회 로직 추가
                         # tx_hash = ...

                     elif actual_cost_type_used == 'sim_cash':
                          # 표준 아이템에 sim_cash가 정의되어 있다면 여기서 처리 (현재는 title_purchase만 sim_cash)
                          # title_purchase는 위에서 특별 처리했으므로 여기에 오지 않아야 함.
                          # 만약 다른 sim_cash 아이템이 있다면 여기에 로직 추가
                          raise ValueError(f"'{item_name}' 아이템은 모의 현금 결제를 지원하지 않습니다.") # 오류 메시지

                     else:
                         # Should not reach here if cost_type_definition is handled
                         raise ValueError(f"'{item_name}' 아이템에 대한 알 수 없는 결제 타입 처리: {actual_cost_type_used}")


                # --- 차감 성공 시, 나머지 효과 적용 (deduction_success가 True일 때만 실행) ---
                # 차감 실패 시는 여기서 예외가 발생해서 트랜잭션 롤백됨.
                if deduction_success:
                    action_success = False # 아이템 효과 적용 성공 플래그
                    # result_message는 이미 위에서 차감 성공 시 설정됨.

                    # === 각 아이템 ID 별 효과 적용 ===
                    # ASI 코인 충전, 칭호 구매, 수익률 비례 전략 구독 등은 효과 적용 로직이
                    # 위에서 이미 차감 로직과 함께 또는 특별 케이스로 처리됨.
                    # 여기서는 그 외 아이템들의 효과를 최종적으로 적용.

                    if item_id == 'cash_refill':
                        # 모의투자 머니 초기화 - 이미 위에서 user.cash 업데이트로 처리됨
                        action_success = True # 차감 성공 시 효과 적용도 성공으로 간주
                        # user_locked.cash 업데이트는 이미 위에서 했음.

                    elif item_id == 'level_xp_1000':
                        # 레벨 경험치 추가 - 이미 위에서 user.level_xp 업데이트로 처리됨
                        action_success = True # 차감 성공 시 효과 적용도 성공으로 간주
                        # TODO: 레벨업 로직 호출 (user_locked.add_level_xp() 같은 함수 사용)

                    elif item_id == 'wl_reset':
                         # 승패 초기화 효과 적용
                         user_locked.total_wins = 0
                         user_locked.total_losses = 0
                         user_locked.save(update_fields=['total_wins', 'total_losses'])
                         action_success = True
                         result_message = result_message or "승패 기록이 초기화되었습니다." # 메시지 중복 방지
                         user_locked.refresh_from_db(fields=['total_wins', 'total_losses']) # 업데이트된 승패 반영

                    elif item_id == 'nickname_color':
                        # 닉네임 색상 변경 로직 - 이미 위에서 user.nickname_color 업데이트로 처리됨
                        # selected_color 유효성 검사는 위에서 했음.
                        # user_locked.nickname_color 업데이트는 위에서 했음.
                        action_success = True # 차감 성공 시 효과 적용도 성공으로 간주
                        # result_message는 이미 위에서 설정됨
                        user_locked.refresh_from_db(fields=['nickname_color']) # 업데이트된 색상 반영


                    elif item_id == 'profile_cosmetic':
                         # 프로필 꾸미기 아이템 효과 적용 로직 (예: 사용자에게 아바타/배경 선택/지급)
                         # TODO: 구현 필요. 어떤 꾸미기 아이템인지 추가 데이터(예: cosmetic_id) 필요할 수 있음.
                         # UserCosmetic.objects.create(user=user_locked, cosmetic_id=...) # 예시
                         action_success = True
                         result_message = result_message or f"'{item_name}' 아이템이 적용되었습니다!" # 메시지


                    elif item_id == 'auto_trade_10h':
                         # 자동매매 시간 충전 - 이미 위에서 시간 추가로 처리됨
                         action_success = True # 차감 성공 시 효과 적용도 성공으로 간주
                         # result_message는 이미 위에서 설정됨
                         user_locked.refresh_from_db(fields=['auto_trade_seconds_remaining']) # 시간 반영


                    # TODO: strategy_sub_profit (수익률 비례 결제) 아이템 효과 로직 구현 (복잡)
                    # 차감은 위에서 이미 되었음. 여기서는 구독 활성화 로직.
                    # 프론트에서 보낸 strategy_id에 대한 구독을 활성화해야 함.
                    # StrategySubscription.objects.create(...)
                    # 이 아이템은 가격 계산과 차감, 그리고 구독 활성화가 한 로직으로 묶여야 더 안전함.
                    # 현재는 차감 후 여기까지 오므로 임시 성공 처리.
                    # elif item_id == 'strategy_sub_profit':
                    #    # TODO: 구독 활성화 로직 구현
                    #    action_success = True
                    #    result_message = result_message or "수익률 비례 전략 구독 완료!"


                    elif item_id in ['asi_refill', 'title_purchase', 'view_trader', 'strategy_page_sub']:
                         # 이 아이템들은 효과 적용 로직이 이미 위 차감 블록에서 특별 처리되었거나 포함됨.
                         # 여기에 다시 로직을 넣을 필요는 없음.
                         action_success = True # 이미 위에서 처리되었다고 가정하고 성공 처리


                    else:
                         # items_info에는 정의되어 있지만 여기서 효과 적용 로직이 누락된 경우
                         # 차감은 이미 되었으므로 환불 로직이 필요하거나, 애초에 효과 적용 로직까지 포함해야 함.
                         print(f"오류: 아이템 ID '{item_id}' 효과 적용 로직 누락 또는 미완성.")
                         # raise NotImplementedError(f"아이템 ID '{item_id}' 효과 적용 로직이 누락되었거나 미완성입니다.") # 개발 중에는 에러 발생
                         # 임시로 차감 성공/효과 적용 누락 메시지를 반환 (실제 서비스에서는 적절한 오류 처리 필요)
                         action_success = False # 효과 적용 실패 (개발자에게 알림)
                         result_message = result_message or f"'{item_name}' 결제는 완료되었으나 효과 적용 로직이 아직 구현되지 않았습니다. 관리자에게 문의하세요."


                    # --- 모든 DB 변경사항 최종 저장 (transaction.atomic으로 묶여있음) ---
                    # save()는 위에서 save(update_fields=...)를 사용했더라도 최종 상태를 보장하기 위해 호출
                    # 특히 effect 로직에서 save를 명시적으로 호출했다면 중복될 수 있지만 트랜잭션 안에서는 괜찮음
                    # user_locked.save()


                else:
                     # 차감은 성공했으나 effect 적용 로직이 없는 아이템이거나 다른 문제로 여기 온 경우
                     # 위에 raise ValueError 등으로 예외가 발생해서 여기 오지 않아야 정상.
                     # 혹시 모를 상황 대비 (대부분 여기에 오지 않아야 함)
                     print(f"오류: 아이템 구매 처리 최종 실패 - 차감 성공={deduction_success}, 효과 적용 성공={action_success}")
                     # 에러 메시지는 이미 위의 except 블록에서 설정되었을 것임.
                     raise ValueError("아이템 구매 처리 중 예기치 않은 오류 발생.") # 트랜잭션 롤백 유도


        # --- Exception Handling within Transaction ---
        except ValueError as ve:
             # Catch specific validation errors and deduction errors (raised as ValueErrors)
             print(f"오류 (ValueError): 아이템 구매 처리 중 오류 ({item_id}) - {ve}")
             # Transaction is rolled back automatically
             return JsonResponse({'success': False, 'message': f"구매 처리 실패: {ve}"}, status=400)
        except NotImplementedError as nie:
             # catch missing effect logic if raised
             print(f"오류 (NotImplementedError): 아이템 효과 적용 로직 누락 ({item_id}) - {nie}")
             return JsonResponse({'success': False, 'message': '서버 내부 오류: 아이템 효과 로직 미구현.'}, status=500)
        except Exception as e: # Catch any other unexpected errors during transaction block
             print(f"오류 (Exception): 아이템 효과 적용 중 예기치 않은 오류 ({item_id}): {e}")
             traceback.print_exc()
             # Transaction is rolled back automatically
             return JsonResponse({'success': False, 'message': '서버 내부 오류가 발생했습니다.'}, status=500)


        # --- Final Success Response ---
        # If code reaches here, both deduction and item effect application were successful
        # 트랜잭션 완료 후, 사용자 객체의 최신 잔액 정보 다시 로드
        user_locked = User.objects.get(pk=user_id) # 트랜잭션 밖에서 새로 가져옴 (락 필요 없음)
        # 또는 위에서 이미 락 걸었던 user_locked 객체를 사용하되, 트랜잭션 밖에서 save/refresh

        # 응답에 포함시킬 최종 잔액 정보 (DecimalField는 JSON 직렬화 시 문자열 될 수 있음. 프론트에서 파싱 필요)
        final_asi_balance = user_locked.asi_coin_balance
        final_real_cash = user_locked.real_cash
        final_sim_cash = user_locked.cash

        # TODO: ASI 출금 시 tx_hash 기록/조회 로직 구현했다면 여기에 포함
        # tx_hash = ... # 트랜잭션 내에서 얻은 해시

        return JsonResponse({
            'success': True,
            'message': result_message or f"'{item_name}' 구매 완료!",
            # 프론트엔드 잔액 업데이트용 최신 잔액 정보 포함 (숫자로 파싱하기 용이하도록 Decimal 유지)
            'new_balance': final_asi_balance, # ASI 잔액 (Decimal)
            'new_real_cash': final_real_cash, # 현금 잔액 (Float/Decimal)
            'new_sim_cash': final_sim_cash, # 모의 현금 잔액 (Float/Decimal)
            # 필요시 사용자 레벨, 티어, 승패 등 업데이트된 정보도 같이 보냄.
            # user_locked 객체에서 가져온 필드들 포함.
            'new_level_xp': user_locked.level_xp,
            'new_level': user_locked.current_level, # @property 값 사용
            'new_user_tier_xp': user_locked.user_tier_xp,
            'new_user_tier_info': user_locked.get_tier_info(), # @property 결과 사용
            'new_total_wins': user_locked.total_wins,
            'new_total_losses': user_locked.total_losses,
            'new_auto_trade_seconds': user_locked.auto_trade_seconds_remaining,
        })


    # --- 최외곽 에러 처리 ---
    except json.JSONDecodeError:
        print("오류: 잘못된 JSON 요청 본문.")
        return JsonResponse({'success': False, 'message': '잘못된 요청 형식입니다.'}, status=400)
    except Exception as e:
        print(f"API 오류 (/api/shop/purchase/): {e}") # 예기치 않은 서버 내부 오류
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': '서버 내부 오류가 발생했습니다.'}, status=500)

# TODO: spend_asi_coin 함수 구현 필요 (User 모델의 asi_coin_balance 차감) - Decimal 사용하도록
# TODO: StrategyPageSubscription, PositionViewSubscription, UserTitle 모델 구현 필요
# TODO: spend_asi_coin 함수 내에서 ASI 출금 연동 및 tx_hash 반환 로직 추가 필요
# TODO: 수익률 비례 전략 구독 가격 계산 및 활성화 로직 구현 (복잡)
# TODO: spend_real_cash, spend_sim_cash 함수가 User 모델 메서드로 구현되어 있다면 여기서 삭제하고 User 모델에서 import하여 사용.
# TODO: User 모델에 current_level, get_tier_info 메서드가 없다면 models.py에 추가.








