from django.shortcuts import render
from django.http import HttpResponse
import requests
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate # 자동 로그인을 위해 login 추가
from django.contrib import messages # 사용자에게 피드백 메시지를 보여주기 위함
from django.db.models import F # DB 업데이트 시 원자적 연산 지원
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import StrategyPageSubscription # 모델 import
from datetime import datetime
from django.urls import reverse
import random
#Holding/Trade 모델이 별도로 있다면 임포트
from .models import Holding


from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse # AJAX 뷰들에서 사용
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import json
import random
from django.core.cache import cache


from .forms import NicknameChangeForm, PositionSharingForm

from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST

from .forms import NICKNAME_BLACKLIST,UserRegistrationForm # 위에서 만든 폼
from .models import User # 실제 User 모델 (get_user_model() 사용 권장)
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST # POST 요청만 허용
from django.contrib.auth.decorators import login_required # 로그인된 사용자만 접근 허용
from django.views.decorators.csrf import csrf_exempt # 주의해서 사용하거나 클라이언트에서 CSRF 처리 필요
from django.contrib.auth import get_user_model # 또는 사용자 정의 User 모델 경로





import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET # GET 요청만 허용
from django.contrib.auth.decorators import login_required # 로그인된 사용자만 접근 허용
from django.forms.models import model_to_dict # 모델 인스턴스를 딕셔너리로 변환
# Traceback import (오류 로깅용)
import traceback


# User 모델 import
from .models import User # 사용자 모델 import
from django.contrib.auth import get_user_model




import requests
import json
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


###############아이템구매

from django.http import JsonResponse
from django.views.decorators.http import require_POST # POST 요청만 받도록
from django.views.decorators.csrf import csrf_exempt # 필요시 CSRF 예외 처리 (JS에서 토큰 보내는것 권장)
from django.contrib.auth.decorators import login_required # 로그인 필수
import json
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.db.models import F # DB 업데이트 시 원자적 연산 지원
from django.contrib.auth import get_user_model

# --- ★★★ 서비스 함수 및 모델 Import (실제 경로로 수정 필수!) ★★★ ---
# spend_asi_coin 함수가 정의된 파일 경로에서 import
# 예: from chart.blockchain_reward import spend_asi_coin
from chart.blockchain_reward import spend_asi_coin # 사용자가 chart 폴더 언급했으므로 임시 적용

# User 모델 및 구독 모델 import (main 앱의 models.py 에 있다고 가정)
# User는 get_user_model() 사용, 구독 모델은 .models 에서 가져오기
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

# TODO: StrategyPageSubscription, PositionViewSubscription, UserTitle 등 모델 import (models.py에 있다면)
from main.models import StrategyPageSubscription, PositionViewSubscription # 예시 import (실제 모델 위치에 맞게)
# TODO: UserTitle 모델 import (models.py에 있다면)



from django.http import JsonResponse
from django.views.decorators.http import require_POST # POST 요청만 받도록
from django.views.decorators.csrf import ensure_csrf_cookie # CSRF 처리 관련 (필요시)
from django.contrib.auth.decorators import login_required
from chart.blockchain_reward import process_trade_result # 코인 보상 업데이트



# 예시: your_app_name/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
from decimal import Decimal, InvalidOperation # Decimal 및 오류 처리 import

# initiate_onchain_withdrawal 함수 import (★ 실제 경로 확인 및 수정 필요 ★)
# 예: from your_project_name.blockchain_service import initiate_onchain_withdrawal
from chart.blockchain_service import initiate_onchain_withdrawal # 임시 경로


# views.py (예시: index2_simulator_page 뷰)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from django.contrib.auth import get_user_model
from .models import Holding # 모델 임포트 가정



GUEST_MAX_USAGE_SECONDS = 1 * 60  # 비로그인 사용자 하루 최대 이용 시간 (1분)
LOGGED_IN_USAGE_FEE = Decimal('0.1')  # 로그인 사용자 시간당 차감 코인
LOGGED_IN_FEE_HOURS_INTERVAL = 1  # 코인 차감 간격 (시간 단위)


def index(request):
    register_form_instance = UserRegistrationForm()
    show_register_modal_on_error = False

    if request.method == 'POST':
        if 'register_submit' in request.POST:  # 회원가입 폼 제출 확인
            print("[INDEX_VIEW] Register form POST 요청 받음")
            register_form_instance = UserRegistrationForm(request.POST)

            is_form_valid = register_form_instance.is_valid()
            print(f"[INDEX_VIEW] register_form.is_valid() 결과: {is_form_valid}")

            if is_form_valid:
                print("[INDEX_VIEW] Register 폼 유효성 검사 1차 통과!")

                # --- 1. 재가입 방지 로직 (사용자 이름 기준) ---
                username_to_check = register_form_instance.cleaned_data.get('username')
                # 휴대폰 번호로도 체크하려면:
                # phone_to_check = register_form_instance.cleaned_data.get('phone_number')

                # is_active=False 인 사용자 중에서 username (또는 phone_number)으로 찾아봄
                # User 모델에 date_deactivated, can_rejoin_at 필드가 있어야 함
                deactivated_user = User.objects.filter(username__iexact=username_to_check, is_active=False).first()
                # 또는 phone_number로 체크:
                # deactivated_user_by_phone = User.objects.filter(phone_number=phone_to_check, is_active=False).first()
                # if not deactivated_user and deactivated_user_by_phone:
                #     deactivated_user = deactivated_user_by_phone

                can_proceed_after_rejoin_check = True  # 다음 단계로 진행 가능 여부 플래그

                if deactivated_user and hasattr(deactivated_user,
                                                'can_rejoin_at') and deactivated_user.can_rejoin_at and timezone.now() < deactivated_user.can_rejoin_at:
                    print(f"[INDEX_VIEW] !!! 재가입 불가 사용자: {username_to_check} !!!")
                    # timezone.localtime()으로 사용자 지역 시간으로 변환 (settings.TIME_ZONE 기준)
                    rejoin_time_local = timezone.localtime(deactivated_user.can_rejoin_at)
                    time_left_str = rejoin_time_local.strftime('%Y년 %m월 %d일 %H시 %M분')

                    # 폼 전체에 대한 오류(non-field error)로 추가
                    register_form_instance.add_error(None, _("이전에 탈퇴한 계정입니다. %(rejoin_time)s 이후에 재가입할 수 있습니다.") % {
                        'rejoin_time': time_left_str})
                    messages.error(request, _("이전에 탈퇴한 계정입니다. 안내된 시간 이후에 재가입해주세요."))
                    show_register_modal_on_error = True
                    can_proceed_after_rejoin_check = False

                if can_proceed_after_rejoin_check:
                    # --- 2. 휴대폰 인증 상태 최종 확인 ---
                    verified_phone_in_session = request.session.get('phone_verified_for_registration')
                    submitted_phone_number = register_form_instance.cleaned_data.get('phone_number')
                    print(f"[INDEX_VIEW] 세션 내 인증된 폰: '{verified_phone_in_session}', 제출된 폰: '{submitted_phone_number}'")

                    if not verified_phone_in_session or verified_phone_in_session != submitted_phone_number:
                        print("[INDEX_VIEW] !!! 휴대폰 인증 실패 또는 불일치 (in index_view) !!!")
                        register_form_instance.add_error('phone_number', _('휴대폰 인증을 먼저 완료해주세요. (인증된 번호와 다를 수 있습니다)'))
                        messages.error(request, _('휴대폰 인증 정보가 올바르지 않습니다. 다시 시도해주세요.'))
                        show_register_modal_on_error = True
                    else:
                        # --- 3. 모든 검증 통과, 사용자 저장 시도 ---
                        print("[INDEX_VIEW] 휴대폰 인증 검증 통과 (in index_view)!")
                        try:
                            print("[INDEX_VIEW] register_form.save(commit=False) 실행 시도...")
                            user = register_form_instance.save(commit=False)
                            print(f"[INDEX_VIEW] User 객체 생성됨: {user.username}")

                            user.phone_number = submitted_phone_number  # 폼에서 받은 인증된 번호로 최종 설정
                            user.phone_verified = True  # User 모델에 이 필드가 있다고 가정
                            print("[INDEX_VIEW] User 객체에 phone_number, phone_verified 설정 완료.")

                            # user.is_active는 UserRegistrationForm.save()에서 True로 설정되거나 모델 기본값 사용

                            print("[INDEX_VIEW] user.save() 실행 시도 (DB에 최종 저장)...")
                            user.save()  # UserRegistrationForm의 save 메서드에서 초기값 등 설정됨
                            print("[INDEX_VIEW] user.save() 성공! DB에 사용자 저장 완료.")

                            request.session.pop('phone_verified_for_registration', None)
                            print("[INDEX_VIEW] 세션에서 phone_verified_for_registration 삭제 완료.")

                            login(request, user)
                            print(f"[INDEX_VIEW] 사용자 {user.username} 자동 로그인 성공.")
                            messages.success(request, _(f'{user.username}님, 회원가입이 완료되었습니다! ASI 플랫폼에 오신 것을 환영합니다.'))
                            print("[INDEX_VIEW] 회원가입 성공! index 페이지로 리디렉션.")
                            return redirect('index')

                        except Exception as e:
                            print(f"[INDEX_VIEW] !!! user.save() 또는 login 중 예외 발생: {e} !!!")
                            import traceback
                            traceback.print_exc()
                            messages.error(request, _('회원가입 처리 중 오류가 발생했습니다. 관리자에게 문의해주세요.'))
                            show_register_modal_on_error = True

            # 이 else는 if register_form_instance.is_valid(): 의 else 입니다.
            # 또는, 위의 if can_proceed_after_rejoin_check: 나 if (휴대폰인증): 의 else 에서
            # show_register_modal_on_error = True 가 설정되었다면 여기까지 올 수 있습니다.
            if not register_form_instance.is_valid() or register_form_instance.errors:  # 폼 자체 유효성 오류 또는 수동 추가된 오류가 있다면
                if not show_register_modal_on_error:  # 위에서 messages.error를 이미 찍지 않은 경우
                    messages.error(request, _('입력하신 정보를 다시 확인해주세요.'))
                show_register_modal_on_error = True
                print("[INDEX_VIEW] !!! Register 폼 유효성 검사 실패 또는 추가 검증 실패 !!!")
                if register_form_instance.errors:
                    print("[INDEX_VIEW] Register 폼 오류 내용:")
                    for field, errors_list in register_form_instance.errors.items():
                        for error in errors_list:
                            print(f"  - 필드 '{field if field != '__all__' else 'Non-field'}': {error}")

        # elif 'login_submit' in request.POST:
        # ... 로그인 폼 처리 로직 ...

    # GET 요청 또는 POST 처리 후 (성공 시 리디렉션, 실패 시 아래로 내려와서 다시 렌더링)
    context = {
        'register_form': register_form_instance,
        'show_register_modal_on_error': show_register_modal_on_error,
        # 'login_form': login_form_instance,
        # ... index_homepage.html에 필요한 다른 모든 컨텍스트 변수들 ...
    }
    return render(request, "main/index_homepage.html", context)

def index2_simulator_backup(request):
    return render(request,"main/index2_simulator.html")

def index2_simulator(request):
    user = request.user

    try:
        # JavaScript용 딕셔너리 생성
        holdings_qs = user.holdings.all()
        holdings_dict_for_js = {}
        for holding in holdings_qs:
            holdings_dict_for_js[holding.symbol] = {
                'quantity': holding.quantity, # 모델 필드 이름 확인! (quantity or stock_count)
                'avgPrice': holding.avg_price,
                'symbol': holding.symbol
            }

        context = {
            'user': user,
            # 생성된 딕셔너리를 JSON 문자열로 변환하여 전달
            'holdings_json_for_js': json.dumps(holdings_dict_for_js)
        }
    except:
        context={'user': user}

    return render(request, 'main/index2_simulator.html', context)


def index2_1(request):
    return render(request,"main/index2_1_past_simulator.html")





















def index3_strategy(request):
    now = timezone.now()
    today_str = now.strftime('%Y-%m-%d')  # 비로그인 사용자 일일 사용량 체크용
    context = {}

    if request.user.is_authenticated:
        # Django의 request.user는 이미 현재 로그인된 User 모델의 인스턴스입니다.
        # 따라서 User.objects.get(pk=request.user.pk)는 보통 필요 없습니다.
        user = request.user

        # --- 사용자의 구독 플랜 확인 ---
        is_premium_user = (user.subscription_plan == '프리미엄')  # 구독플랜에 따라 숨김처리함(index3 에서)
        is_basic_or_higher_subscriber = user.subscription_plan in ['베이직', '스탠다드', '프리미엄']
        if is_basic_or_higher_subscriber:
            LOGGED_IN_USAGE_FEE = Decimal('0.0') # 무료등급이 아니면(구독상태면) 코인 차감 x
        else:
            LOGGED_IN_USAGE_FEE = Decimal('0.0') # 무료등급인경우 (코인차감)
        context['is_premium_user'] = is_premium_user

        # --- 베이직 등급 이상 접근 가능 로직 (만약 이 페이지 자체가 특정 등급 이상만 접근 가능하다면) ---
        # 예시: if user.subscription_plan not in ['BASIC', 'STANDARD', 'PREMIUM']:
        #           messages.error(request, "AI 트레이더 페이지는 베이직 등급 이상부터 접근 가능합니다.")
        #           return redirect('some_subscription_info_page_url_name')

        # --- 기존 코인 차감 로직 (페이지 로드 시) ---
        should_deduct_coin_on_load = False
        last_fee_time = user.last_strategy_page_fee_time  # User 모델에 이 필드가 있다고 가정

        if last_fee_time is None:  # 첫 방문 또는 요금 정책 변경 후 첫 방문
            should_deduct_coin_on_load = True
        else:
            if (now - last_fee_time) >= timedelta(hours=LOGGED_IN_FEE_HOURS_INTERVAL):
                should_deduct_coin_on_load = True

        if should_deduct_coin_on_load:

            original_balance = user.asi_coin_balance  # 차감 전 잔액 (선택적 로깅용)
            if hasattr(user, 'spend_asi_coin') and callable(user.spend_asi_coin):
                can_spend = user.spend_asi_coin(LOGGED_IN_USAGE_FEE)  # User 모델의 메서드 사용
            else:  # 만약 spend_asi_coin 메서드가 없다면 직접 처리 (이전 코드 참고)
                if user.asi_coin_balance >= LOGGED_IN_USAGE_FEE:
                    user.asi_coin_balance -= LOGGED_IN_USAGE_FEE
                    can_spend = True
                else:
                    can_spend = False

            if can_spend:
                user.last_strategy_page_fee_time = now  # 차감 성공 시 시간 업데이트
                # spend_asi_coin 메서드가 잔액 변경 후 save를 안했다면, 여기서 함께 저장
                user.save(update_fields=['asi_coin_balance', 'last_strategy_page_fee_time'])
                messages.success(request,
                                 _(f"{LOGGED_IN_USAGE_FEE} ASI 코인이 사용되었습니다. (현재 잔액: {user.asi_coin_balance.quantize(Decimal('0.0001'))})"))
                last_fee_time = now  # 다음 시간 계산을 위해 업데이트
            else:
                if not is_basic_or_higher_subscriber:
                    messages.error(request, _("ASI 코인이 부족합니다. 3일 무료 체험을 하시려면 카드를 등록해주세요."))
                    try:
                        add_card_page_url = reverse('add_card')  # <<< 카드 등록 페이지 URL로 변경
                    except Exception:
                        add_card_page_url = '/payment/add-card/'
                    context['show_charge_ASI_popup'] = True
                    context['marketing_page_url_for_popup'] = add_card_page_url

                messages.error(request, _("ASI 코인이 부족합니다. 충전해주세요."))
                from django.urls import reverse, NoReverseMatch
                try:
                    marketing_url = reverse('index4_user_market')
                    print(f"[INDEX3_STRATEGY] 성공적으로 URL 리버스: 'index4_user_market' -> '{marketing_url}'")
                except NoReverseMatch as e:  # NoReverseMatch 오류를 구체적으로 잡음
                    print(f"[INDEX3_STRATEGY] !!! NoReverseMatch 오류 발생 ('index4_user_market'): {e} !!!")
                    marketing_url = '/index4/'  #
                except Exception as e:  # 그 외 다른 예외
                    print(f"[INDEX3_STRATEGY] !!! 'index4_user_market' 리버스 중 기타 예외 발생: {e} !!!")
                    marketing_url = '/index4/'  # f

                context['show_charge_ASI_popup'] = True  # JavaScript에서 이 값으로 팝업 제어
                context['marketing_page_url_for_popup'] = marketing_url

        # 다음 코인 차감까지 남은 시간 계산
        if last_fee_time:
            next_deduction_time_obj = last_fee_time + timedelta(hours=LOGGED_IN_FEE_HOURS_INTERVAL)
            if next_deduction_time_obj > now:
                context['time_until_next_deduction_seconds'] = (next_deduction_time_obj - now).total_seconds()
            else:  # 이미 차감 시간이 지났거나 정확히 차감 시간
                context['time_until_next_deduction_seconds'] = timedelta(
                    hours=LOGGED_IN_FEE_HOURS_INTERVAL).total_seconds()
        else:
            # 첫 사용이고, 코인이 부족해서 위에서 차감이 안됐다면 last_fee_time은 여전히 None
            # 이 경우, 다음에 올바른 시간 표시를 위해 전체 간격으로 설정 (또는 0으로 설정하여 즉시 API 호출 유도)
            context['time_until_next_deduction_seconds'] = timedelta(hours=LOGGED_IN_FEE_HOURS_INTERVAL).total_seconds()

        context['user_asi_coin_balance'] = user.asi_coin_balance.quantize(Decimal("0.0001"))

        # --- AI 트레이더 리스트 및 각 트레이더의 수익률 정보 등 context에 추가 ---
        # 예시: context['traders_summary'] = get_traders_summary_for_template(user, is_premium_user)
        # 이 함수는 각 트레이더의 기본 정보와 함께, 프리미엄이 아니면 "실시간 포지션 값" 등을
        # 모자이크 처리된 값이나 플레이스홀더로 설정해서 반환할 수 있습니다.
        # (이 부분은 실제 데이터 구조와 로직에 따라 구현 필요)

    else:  # 비로그인 사용자 처리
        session_key_first_visit_time_today = f'guest_first_visit_time_{today_str}'

        if session_key_first_visit_time_today not in request.session:
            request.session[session_key_first_visit_time_today] = now.isoformat()
            # request.session.set_expiry(timedelta(days=1)) # 세션 만료 설정 (선택 사항)
            print(f"비로그인 사용자 첫 방문 또는 날짜 변경: {today_str}. 세션 초기화.")

        first_visit_time_iso = request.session.get(session_key_first_visit_time_today)  # .get() 사용
        if not first_visit_time_iso:  # 혹시 세션 값이 없을 경우 대비 (거의 발생 안 함)
            request.session[session_key_first_visit_time_today] = now.isoformat()
            first_visit_time_iso = now.isoformat()

        first_visit_time = datetime.fromisoformat(first_visit_time_iso)
        # first_visit_time이 naive이면 aware로 변환 (settings.USE_TZ=True일 경우 now는 aware)
        if timezone.is_naive(first_visit_time) and timezone.is_aware(now):
            first_visit_time = timezone.make_aware(first_visit_time, timezone.get_default_timezone())

        current_total_usage_seconds = (now - first_visit_time).total_seconds()
        print(f"비로그인 사용자: 오늘 사용 시간 {current_total_usage_seconds:.0f}초 / {GUEST_MAX_USAGE_SECONDS}초")

        if current_total_usage_seconds >= GUEST_MAX_USAGE_SECONDS:
            messages.info(request, _("비로그인 사용자의 하루 무료 이용 시간이 모두 소진되었습니다. 로그인 후 계속 이용해주세요."))
            try:
                # allauth를 사용 중이라면 account_login이 일반적
                login_url = reverse('account_login')  # 또는 직접 정의한 'login' URL 이름
            except Exception:
                login_url = '/accounts/login/'  # 또는 실제 로그인 페이지 경로
            return redirect(login_url)

        remaining_time = GUEST_MAX_USAGE_SECONDS - current_total_usage_seconds
        context['guest_remaining_time_seconds'] = max(0, remaining_time)
        # 비로그인 사용자에게도 is_premium_user는 False로 전달 (템플릿에서 분기 처리 위함)
        context['is_premium_user'] = False

    return render(request, "main/index3_strategy.html", context)




try:
    from payments.models import UserPaymentMethod # payments 앱의 모델이라고 가정
    from .models import Title
except ImportError:
    UserPaymentMethod = None
    print("경고: payments.models에서 UserPaymentMethod를 찾을 수 없습니다. (index4_user_market)")

from django.contrib.auth import get_user_model
User = get_user_model()

@login_required
def index4_user_market(request):
    user = request.user
    has_payment_method = False
    payment_method_details_for_template = None

    if UserPaymentMethod:
        try:
            payment_info = UserPaymentMethod.objects.get(user=user, is_default=True)
            if payment_info and payment_info.pg_customer_id:
                has_payment_method = True
                payment_method_details_for_template = {
                    'brand': payment_info.card_brand,
                    'last4': payment_info.last4
                }
        except UserPaymentMethod.DoesNotExist:
            pass
        except AttributeError:
            pass

    # 구독 플랜 정보 (실제로는 DB 또는 설정에서 관리)
    plans_info_for_template = [
        {'id': 'basic', 'name_kr': '베이직', 'price_krw': 3900, 'currency': 'KRW', 'description_key': 'plan_basic_desc'},
        {'id': 'standard', 'name_kr': '스탠다드', 'price_krw': 6900, 'currency': 'KRW', 'description_key': 'plan_standard_desc'},
        {'id': 'premium', 'name_kr': '프리미엄', 'price_krw': 19900, 'currency': 'KRW', 'description_key': 'plan_premium_desc'},
    ]

    # 상점 아이템 정보 (현금 가격은 data-* 속성 또는 여기서 전달)
    # 실제 아이템 정보는 DB에서 가져오는 것이 좋습니다.
    shop_items_for_template = [
        {'id': 'cash_refill', 'name_kr': '모의투자 머니 초기화', 'price_asi': 10, 'price_cash': 10000, 'currency': 'KRW', 'description_key': 'item_cash_refill_desc'},
        {'id': 'asi_refill', 'name_kr': 'ASI 코인 충전', 'price_cash_per_unit': 1000, 'currency': 'KRW', 'description_key': 'item_asi_refill_desc'}, # 수량 기반
        {'id': 'wl_reset', 'name_kr': '승패 초기화', 'price_asi': 4, 'price_cash': 4000, 'currency': 'KRW', 'description_key': 'item_wl_reset_desc'},
        {'id': 'nickname_color', 'name_kr': '닉네임 색상 변경권', 'price_asi': 1, 'price_cash': 1000, 'currency': 'KRW', 'description_key': 'item_nickname_color_desc'},
        {'id': 'level_xp_1000', 'name_kr': '레벨 경험치 +1000', 'price_asi': Decimal('0.1'), 'price_cash': 100, 'currency': 'KRW', 'description_key': 'item_level_xp_1000_desc'},
        # ... 기타 아이템들 ...
    ]

    purchasable_titles_list = []  # 기본 빈 리스트
    if Title:  # Title 모델이 import 되었을 때만 실행
        purchasable_titles_list = Title.objects.filter(is_purchasable=True).order_by('order')
        print(f"DEBUG [views.py - index4]: 조회된 purchasable_titles 목록: {list(purchasable_titles_list)}")
        print(f"DEBUG [views.py - index4]: 조회된 purchasable_titles 개수: {len(purchasable_titles_list)}")
    else:
        print("DEBUG [views.py - index4]: Title 모델을 찾을 수 없어 칭호 목록을 가져오지 못했습니다.")


    context = {
        'user_is_authenticated_js': True,
        'has_payment_method_js': has_payment_method,
        'payment_method_details_for_template': payment_method_details_for_template,

        'add_card_url_js': reverse('payments:add_card'), # payments 앱 네임스페이스 사용 가정
        'create_subscription_url_js': reverse('payments:create_subscription'),
        'charge_item_card_url_js': reverse('payments:charge_item_card'),
        'purchase_item_asi_url_js': reverse('purchase_item_api'), # 기존 ASI 코인 결제 API URL

        'iamport_store_id_js': getattr(settings, 'IAMPORT_STORE_ID', ''),
        'plans_info_for_template': plans_info_for_template,
        'shop_items_for_template': shop_items_for_template,

        'purchasable_titles': purchasable_titles_list,  # 조회한 칭호 목록을 context에 추가
        'N_DAYS_FREE_TRIAL': getattr(settings, 'N_DAYS_FREE_TRIAL', 3),  # 템플릿에서 사용하므로 추가

    }
    return render(request, 'main/index4_user_market.html', context)

def index5_community(request):
    return render(request,"main/index5_community.html")

def marketing_page(request):
    return render(request,"main/marketing_page.html")






# 코인차감 로직 (페이지 접속 시간 지나면)
@login_required  # 이 API는 로그인한 사용자만 호출 가능
def trigger_coin_deduction_api(request):
    if request.method == 'POST':  # POST 요청만 처리 (CSRF 처리 필요할 수 있음)
        user = User.objects.get(pk=request.user.pk)  # 최신 사용자 정보 가져오기
        now = timezone.now()

        # 코인 차감 조건 확인 (index3_strategy 뷰와 유사 로직)
        should_deduct_coin_now = False
        if user.last_strategy_page_fee_time is None:
            should_deduct_coin_now = True
        else:
            if (now - user.last_strategy_page_fee_time) >= timedelta(hours=LOGGED_IN_FEE_HOURS_INTERVAL):
                should_deduct_coin_now = True

        if not should_deduct_coin_now:
            # 아직 차감 시간이 안 됐으면, 현재 상태만 반환 (또는 에러 메시지)
            next_deduction_time = user.last_strategy_page_fee_time + timedelta(hours=LOGGED_IN_FEE_HOURS_INTERVAL)
            time_until_next = next_deduction_time - now
            return JsonResponse({
                'status': 'no_deduction_needed',
                'message': '아직 코인 차감 시간이 아닙니다.',
                'current_asi_coin_balance': str(user.asi_coin_balance.quantize(Decimal("0.0001"))),  # 소수점 4자리까지
                'new_time_until_next_deduction_seconds': time_until_next.total_seconds() if time_until_next.total_seconds() > 0 else 0,
            })

        # 코인 차감 시도 (User.spend_asi_coin 메서드가 boolean만 반환한다고 가정)
        can_spend = user.spend_asi_coin(LOGGED_IN_USAGE_FEE)

        if can_spend:
            user.last_strategy_page_fee_time = now
            user.save(update_fields=['last_strategy_page_fee_time'])

            new_next_deduction_time = now + timedelta(hours=LOGGED_IN_FEE_HOURS_INTERVAL)
            new_time_until_next_seconds = (new_next_deduction_time - now).total_seconds()

            return JsonResponse({
                'status': 'success',
                'message': f"{LOGGED_IN_USAGE_FEE} ASI 코인이 사용되었습니다. (현재 잔액: {user.asi_coin_balance.quantize(Decimal('0.0001'))})",
                'current_asi_coin_balance': str(user.asi_coin_balance.quantize(Decimal("0.0001"))),
                'new_time_until_next_deduction_seconds': new_time_until_next_seconds,
            })
        else:  # 코인 부족
            marketing_url = ''
            try:
                marketing_url = reverse('marketing_page')
            except Exception:
                marketing_url = '/default-marketing-page-if-url-fails/'

            return JsonResponse({
                'status': 'error',
                'message': "ASI 코인이 부족합니다. 충전해주세요.",
                'current_asi_coin_balance': str(user.asi_coin_balance.quantize(Decimal("0.0001"))),
                'redirect_url_if_needed': marketing_url,  # 마케팅 페이지 URL 전달
            }, status=400)  # 클라이언트 에러 상태 코드

    return JsonResponse({'status': 'error', 'message': '잘못된 요청입니다.'}, status=405)  # POST 아니면 에러


def chat_return(request): #채팅을 리턴
    data = request.POST.get("message")
    print(data,'채팅창에 입력된 문자')
    return HttpResponse(data)


# register_view가 모달이 포함된 페이지(예: index_homepage.html)를 렌더링할 때 필요한
# 다른 컨텍스트 변수들을 가져오는 함수가 있다면 여기서 호출하거나,
# index_view에서 POST를 처리하는 것이 더 나을 수 있습니다.
# def get_common_context_for_index_page(request):
#     return { ... }


def register_view(request):
    template_name_with_modal = "main/index_homepage.html"

    print("\n" + "=" * 50)  # 요청 시작 구분선
    print(f"[REGISTER_VIEW] 현재 요청 메소드: {request.method}")

    if request.method == 'POST':
        print("[REGISTER_VIEW] POST 요청 진입")
        form = UserRegistrationForm(request.POST)

        is_form_valid = form.is_valid()
        print(f"[REGISTER_VIEW] form.is_valid() 호출 결과: {is_form_valid}")

        if is_form_valid:
            print("[REGISTER_VIEW] 폼 유효성 검사 통과!")

            verified_phone_in_session = request.session.get('phone_verified_for_registration')
            submitted_phone_number = form.cleaned_data.get('phone_number')
            print(f"[REGISTER_VIEW] 세션 내 인증된 폰: '{verified_phone_in_session}', 제출된 폰: '{submitted_phone_number}'")

            if not verified_phone_in_session or verified_phone_in_session != submitted_phone_number:
                print("[REGISTER_VIEW] !!! 휴대폰 인증 실패 또는 불일치 !!!")
                form.add_error('phone_number', _('휴대폰 인증을 먼저 완료해주세요. (인증된 번호와 다를 수 있습니다)'))
                messages.error(request, _('휴대폰 인증 정보가 올바르지 않습니다. 다시 시도해주세요.'))
                # 오류가 있는 폼으로 다시 렌더링 (아래 공통 부분에서 처리)
            else:
                print("[REGISTER_VIEW] 휴대폰 인증 검증 통과!")
                try:
                    print("[REGISTER_VIEW] form.save(commit=False) 실행 시도...")
                    user = form.save(commit=False)
                    print(f"[REGISTER_VIEW] form.save(commit=False) 실행 완료. User 객체 생성됨: {user.username}")

                    user.phone_number = submitted_phone_number
                    user.phone_verified = True
                    print(f"[REGISTER_VIEW] User 객체에 phone_number, phone_verified 설정 완료.")

                    print("[REGISTER_VIEW] user.save() 실행 시도 (DB에 최종 저장)...")
                    user.save()
                    print("[REGISTER_VIEW] user.save() 성공! DB에 사용자 저장 완료.")

                    request.session.pop('phone_verified_for_registration', None)
                    print("[REGISTER_VIEW] 세션에서 phone_verified_for_registration 삭제 완료.")

                    login(request, user)
                    print(f"[REGISTER_VIEW] 사용자 {user.username} 자동 로그인 성공.")
                    messages.success(request, _(f'{user.username}님, 회원가입이 완료되었습니다! ASI 플랫폼에 오신 것을 환영합니다.'))
                    print("[REGISTER_VIEW] 회원가입 성공! index 페이지로 리디렉션.")
                    return redirect('index')

                except Exception as e:
                    print(f"[REGISTER_VIEW] !!! user.save() 또는 login 중 예외 발생: {e} !!!")
                    import traceback
                    traceback.print_exc()  # 예외의 상세 내용 출력
                    messages.error(request, _('회원가입 처리 중 오류가 발생했습니다. 관리자에게 문의해주세요.'))
                    # form.add_error(None, _('알 수 없는 오류로 가입에 실패했습니다.')) # 이미 form 객체가 아닐 수 있음
                    # 오류 발생 시에도 폼 정보를 포함하여 페이지를 다시 렌더링할 수 있도록 context 구성
                    # 이 경우의 form은 is_valid()를 통과한 상태의 form.
                    context = {
                        'register_form': form,
                        'show_register_modal_on_error': True,
                    }
                    return render(request, template_name_with_modal, context)
        else:  # form.is_valid()가 False인 경우
            print("[REGISTER_VIEW] !!! 폼 유효성 검사 실패 !!!")
            print("[REGISTER_VIEW] 폼 오류 내용:")
            # 폼 오류를 보기 쉽게 출력
            for field, errors in form.errors.items():
                print(f"  - 필드 '{field}': {', '.join(errors)}")

            messages.error(request, _('입력하신 정보를 다시 확인해주세요.'))
            context = {
                'register_form': form,
                'show_register_modal_on_error': True,
            }
            return render(request, template_name_with_modal, context)

    # GET 요청 시
    else:
        print("[REGISTER_VIEW] GET 요청 받음. 빈 폼으로 모달을 띄우기 위해 index로 리디렉션 (또는 index 뷰에서 빈 폼 전달).")
        # 이 뷰가 직접 빈 폼을 렌더링하려면 아래 주석 해제 및 수정
        # form = UserRegistrationForm()
        # context = {'register_form': form}
        # return render(request, template_name_with_modal, context)
        return redirect('index')



@login_required
def profile(request):
    # 이 뷰 함수는 로그인된 사용자만 접근할 수 있도록
    return redirect('index')


# --- 닉네임 중복 및 금칙어 확인 AJAX 뷰 ---
@require_GET
def check_nickname_view(request):
    nickname = request.GET.get('nickname')

    if not nickname:
        return JsonResponse({'status': 'error', 'message': _('닉네임을 입력해주세요.')}, status=400)

    # 이제 forms.py에서 가져온 NICKNAME_BLACKLIST를 사용합니다.
    for forbidden_word in NICKNAME_BLACKLIST:
        if forbidden_word.lower() in nickname.lower():
            return JsonResponse({'status': 'unavailable', 'message': _('선택하신 닉네임에는 사용할 수 없는 단어가 포함되어 있습니다: %(word)s') % {'word': forbidden_word}})

    if User.objects.filter(nickname__iexact=nickname).exists():
        return JsonResponse({'status': 'unavailable', 'message': _('이미 사용 중인 닉네임입니다.')})

    return JsonResponse({'status': 'available', 'message': _('사용 가능한 닉네임입니다.')})

@require_GET
def check_username_view(request):
    username = request.GET.get('username')
    if not username:
        return JsonResponse({'status': 'error', 'message': _('아이디를 입력해주세요.')}, status=400)

    # User 모델의 username 필드는 unique=True이므로, 이 검사가 핵심입니다.
    if User.objects.filter(username__iexact=username).exists(): # iexact: 대소문자 구분 없이 정확히 일치
        return JsonResponse({'status': 'unavailable', 'message': _('이미 사용 중인 아이디입니다.')})
    else:
        # 여기에 추가적인 아이디 형식 유효성 검사를 넣을 수 있습니다.
        # (예: Django User 모델의 기본 username validator 규칙 - 영문, 숫자, @/./+/-/_ 만 허용 등)
        # from django.contrib.auth.validators import UnicodeUsernameValidator
        # username_validator = UnicodeUsernameValidator()
        # try:
        #     username_validator(username)
        # except forms.ValidationError as e:
        #     return JsonResponse({'status': 'invalid', 'message': '; '.join(e.messages)})
        return JsonResponse({'status': 'available', 'message': _('사용 가능한 아이디입니다.')})




# --- 휴대폰 인증번호 발송 AJAX 뷰 ---
@require_POST  # 보안상 POST가 더 적절
def send_otp_view(request):
    try:
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': _('잘못된 요청 형식입니다.')}, status=400)

    if not phone_number:  # TODO: 휴대폰 번호 형식 검증 추가
        return JsonResponse({'status': 'error', 'message': _('휴대폰 번호를 올바르게 입력해주세요.')}, status=400)

    # TODO: 특정 번호/IP로 단시간 내 너무 많은 요청 제한 (Rate Limiting)
    # 예: 1분에 1회, 10분에 3회 등

    otp_code = str(random.randint(100000, 999999))
    otp_key_code = f"otp_code_{phone_number}"
    otp_key_expiry = f"otp_expiry_{phone_number}"
    otp_key_try_count = f"otp_try_count_{phone_number}"  # 인증 시도 횟수 키

    # 캐시 또는 세션에 OTP와 유효 시간(예: 3분) 저장
    cache.set(otp_key_code, otp_code, timeout=180)  # OTP 코드, 180초
    cache.set(otp_key_expiry, (timezone.now() + timedelta(minutes=3)).isoformat(), timeout=185)  # 만료 시간, 약간 더 길게
    cache.set(otp_key_try_count, 0, timeout=185)  # 시도 횟수 초기화

    # TODO: 실제 SMS 발송 로직 구현 (외부 API 연동)
    # from .sms_services import send_sms_message # 예시
    # sms_sent = send_sms_message(phone_number, f"[ASI플랫폼] 인증번호: {otp_code} 유효시간 3분.")
    sms_sent = True  # 임시로 성공 처리
    print(f"Sending OTP: {otp_code} to {phone_number}")  # 개발 중 콘솔 출력

    if sms_sent:
        return JsonResponse({'status': 'success', 'message': _('인증번호가 발송되었습니다.')})
    else:
        return JsonResponse({'status': 'error', 'message': _('SMS 발송에 실패했습니다. 잠시 후 다시 시도해주세요.')})


# --- 휴대폰 인증번호 확인 AJAX 뷰 ---
@require_POST
def verify_otp_view(request):
    try:
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        otp_received = data.get('otp')
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': _('잘못된 요청 형식입니다.')}, status=400)

    if not phone_number or not otp_received:
        return JsonResponse({'status': 'error', 'message': _('휴대폰 번호와 인증번호를 모두 입력해주세요.')}, status=400)

    otp_key_code = f"otp_code_{phone_number}"
    otp_key_expiry = f"otp_expiry_{phone_number}"
    otp_key_try_count = f"otp_try_count_{phone_number}"

    stored_otp_code = cache.get(otp_key_code)
    stored_expiry_str = cache.get(otp_key_expiry)
    try_count = cache.get(otp_key_try_count, 0)

    # 최대 시도 횟수 제한 (예: 5회)
    MAX_OTP_TRY_COUNT = 5
    if try_count >= MAX_OTP_TRY_COUNT:
        return JsonResponse({'status': 'error', 'message': _('인증 시도 횟수를 초과했습니다. 잠시 후 다시 시도해주세요.')})

    if stored_otp_code and stored_expiry_str:
        stored_expiry = timezone.datetime.fromisoformat(stored_expiry_str)
        if timezone.now() > stored_expiry:
            # 만료된 경우
            cache.delete(otp_key_code)
            cache.delete(otp_key_expiry)
            cache.delete(otp_key_try_count)
            return JsonResponse({'status': 'error', 'message': _('인증 시간이 만료되었습니다.')})

        if stored_otp_code == otp_received:
            # 인증 성공
            cache.delete(otp_key_code)  # 성공 시 OTP 삭제 (재사용 방지)
            cache.delete(otp_key_expiry)
            cache.delete(otp_key_try_count)
            request.session['phone_verified_for_registration'] = phone_number  # 세션에 인증된 번호 저장
            return JsonResponse({'status': 'success', 'message': _('인증에 성공했습니다.')})
        else:
            # 인증 실패
            cache.set(otp_key_try_count, try_count + 1,
                      timeout=(stored_expiry - timezone.now()).total_seconds())  # 남은 시간동안 유효
            return JsonResponse({'status': 'error', 'message': _('인증번호가 올바르지 않습니다.')})
    else:
        # OTP가 없거나 만료 정보가 없는 경우 (비정상)
        return JsonResponse({'status': 'error', 'message': _('인증번호를 다시 요청해주세요.')})



User = get_user_model() # 현재 활성화된 User 모델 가져오기

@login_required # 로그인 필수 데코레이터
@require_POST   # POST 요청 필수 데코레이터
# @csrf_exempt # API 엔드포인트에 빠른 방법이지만, 보안상 취약함.
               # 더 나은 방법: Fetch 요청 시 CSRF 토큰 전송 (3단계 참조).
               # csrf_exempt 사용 시 다른 방식으로 CSRF 보호 필요.

def update_portfolio_api(request):
    """
    클라이언트로부터 포트폴리오 전체 상태를 수신하여
    데이터베이스에 저장(동기화)하는 API 엔드포인트.
    """
    try:
        # 1. 현재 로그인된 사용자 객체 가져오기
        user = request.user

        # 2. 클라이언트에서 보낸 JSON 데이터 파싱하기
        if not request.body:
            print(f"오류: 사용자 {user.username} 요청 본문 비어있음.")
            return JsonResponse({'status': 'error', 'message': '요청 본문이 비어있습니다.'}, status=400)

        try:
            # 요청 본문을 UTF-8로 디코딩 시도 (일반적)
            data = json.loads(request.body.decode('utf-8'))
            print(f"로그: 사용자 {user.username} 포트폴리오 데이터 수신: {data}") # 디버깅: 수신 데이터 확인
        except json.JSONDecodeError:
            print(f"오류: 사용자 {user.username} 잘못된 JSON 수신: {request.body[:200]}...") # 앞부분만 로깅
            return JsonResponse({'status': 'error', 'message': '잘못된 JSON 형식입니다.'}, status=400)
        except UnicodeDecodeError:
             print(f"오류: 사용자 {user.username} 요청 본문 디코딩 실패.")
             return JsonResponse({'status': 'error', 'message': '요청 인코딩 오류입니다.'}, status=400)


        # 3. 데이터 추출 및 기본 유효성 검사 (필요시 강화)
        # 클라이언트 데이터를 직접 신뢰하는 것은 보안상 위험할 수 있습니다.
        # 서버에서 재계산 가능한 값(예: portfolio_value)은 가능하면 서버에서 계산하는 것이 좋습니다.

        cash = data.get('cash') # get() 사용으로 키 부재 시 None 반환
        holdings_data = data.get('holdings', {}) # 기본값 빈 딕셔너리
        trades_data = data.get('trades', [])     # 기본값 빈 리스트
        # level = data.get('level') # User 모델에 level 필드가 있다면
        user_tier = data.get('tier') # User 모델에 user_tier 필드가 있다면
        # real_cash = data.get('realCash') # 서버에서 관리 권장
        portfolio_value_client = data.get('portfolioValue') # 클라이언트가 계산한 값

        # 4. 데이터베이스 업데이트 (원자적 트랜잭션 사용)
        try:
            with transaction.atomic():
                # 4.1 User 객체 잠금 및 업데이트 (동시성 문제 방지)
                user_locked = User.objects.select_for_update().get(pk=user.pk)

                update_fields_user = [] # User 모델 업데이트 필드 추적

                # 현금 업데이트 (숫자인지, 음수 아닌지 등 검증 추가 가능)
                if cash is not None and isinstance(cash, (int, float)):
                    user_locked.cash = cash
                    update_fields_user.append('cash')
                # else: # 값이 없거나 타입이 안맞으면 로깅 또는 에러 처리
                #     print(f"경고: 사용자 {user.username}의 cash 값이 유효하지 않음: {cash}")

                # 티어 업데이트 (문자열인지, 유효한 값인지 검증 추가 가능)
                if user_tier is not None and isinstance(user_tier, str):
                    user_locked.user_tier = user_tier # user_tier 필드 존재 가정
                    update_fields_user.append('user_tier')

                # Level 업데이트 (User 모델에 level 필드가 있다면)
                # if level is not None and isinstance(level, int):
                #     user_locked.level = level
                #     update_fields_user.append('level')

                # 포트폴리오 가치 (클라이언트 값 저장 vs 서버 재계산)
                # 여기서는 일단 클라이언트 값 저장, 추후 서버 재계산 로직 추가 권장
                if portfolio_value_client is not None and isinstance(portfolio_value_client, (int, float)):
                     user_locked.portfolio_value = portfolio_value_client # portfolio_value 필드 존재 가정
                     update_fields_user.append('portfolio_value')

                # User 모델 필드 변경사항 저장 (변경된 필드만)
                if update_fields_user:
                    user_locked.save(update_fields=update_fields_user)
                    print(f"로그: 사용자 {user.username} User 모델 업데이트 완료: {update_fields_user}")


                # 4.2 보유 종목(Holdings) 업데이트
                # 현재 방식: 기존 보유 종목 전체 삭제 후, 클라이언트 데이터 기준으로 새로 생성
                # 장점: 구현 간단 / 단점: 매번 삭제/생성으로 비효율적일 수 있음, ID 변경 가능성

                user_locked.holdings.all().delete() # User 모델의 related_name='holdings' 사용
                print(f"로그: 사용자 {user.username} 기존 Holding 레코드 삭제 완료.")

                new_holdings_to_create = [] # 벌크 생성을 위한 리스트
                total_stock_value_server = 0 # 서버에서 평가액 계산용 (선택적)

                # 클라이언트에서 받은 holdings_data 순회
                for symbol, holding_info in holdings_data.items():
                    # 데이터 유효성 검사 강화
                    quantity = holding_info.get('quantity')
                    avg_price = holding_info.get('avgPrice')
                    symbol_str = str(symbol) # 심볼 문자열 확인

                    # 수량은 양수, 평균가는 0 이상인 경우만 처리
                    if (isinstance(quantity, int) and quantity > 0 and
                        isinstance(avg_price, (int, float)) and avg_price >= 0):

                        # 새 Holding 객체 생성 (아직 DB 저장 안 함)
                        new_holdings_to_create.append(Holding(
                            user=user_locked, # 잠금된 사용자 객체 사용
                            symbol=symbol_str,
                            quantity=quantity,
                            avg_price=avg_price
                        ))
                        # 서버에서 평가액 계산 로직 (get_current_price 함수 필요)
                        # current_price = get_current_price(symbol_str) # 가정
                        # total_stock_value_server += quantity * current_price
                    else:
                         print(f"경고: 사용자 {user.username}의 종목 {symbol} 데이터 유효하지 않음 - 건너<0xEB><0x9B><0x81>. Info: {holding_info}")

                # 준비된 Holding 객체들을 한 번에 DB에 생성 (효율적)
                if new_holdings_to_create:
                    Holding.objects.bulk_create(new_holdings_to_create)
                    print(f"로그: 사용자 {user.username} 새로운 Holding 레코드 {len(new_holdings_to_create)}개 생성 완료.")

                # (선택적) 서버에서 재계산한 포트폴리오 가치 업데이트
                # user_locked.portfolio_value = user_locked.cash + total_stock_value_server
                # user_locked.save(update_fields=['portfolio_value'])

                # 4.3 거래 내역(Trades) 추가 (Trade 모델이 있다고 가정)
                # 이 부분은 클라이언트에서 *새로운* 거래 내역만 보낸다고 가정
                # 또는 전체 거래 내역을 보내면 중복 체크 후 저장하는 로직 필요
                # new_trades_to_create = []
                # for trade_info in trades_data:
                #     # trade_info 유효성 검사 (필수 필드: symbol, action, quantity, price, timestamp 등)
                #     if (trade_info.get('symbol') and trade_info.get('action') in ['buy', 'sell'] and
                #         trade_info.get('quantity') > 0 and trade_info.get('price') >= 0 and trade_info.get('timestamp')):
                #         # Trade 모델 객체 생성
                #         new_trades_to_create.append(Trade(
                #             user=user_locked,
                #             symbol=trade_info['symbol'],
                #             action=trade_info['action'],
                #             quantity=trade_info['quantity'],
                #             price=trade_info['price'],
                #             timestamp=trade_info['timestamp'] # 타임스탬프 형식 변환 필요할 수 있음
                #             # ... 기타 필드 ...
                #         ))
                #     else:
                #         print(f"경고: 사용자 {user.username}의 거래 내역 데이터 유효하지 않음: {trade_info}")
                #
                # if new_trades_to_create:
                #      Trade.objects.bulk_create(new_trades_to_create)
                #      print(f"로그: 사용자 {user.username} 새로운 Trade 레코드 {len(new_trades_to_create)}개 생성 완료.")

            # 트랜잭션 성공적으로 완료

        except Exception as db_error:
            # 트랜잭션 내에서 오류 발생 시 롤백됨
            print(f"오류: 사용자 {user.username} DB 업데이트 중 오류 발생 (롤백됨): {db_error}")
            traceback.print_exc()
            return JsonResponse({'status': 'error', 'message': f'데이터베이스 처리 중 오류 발생: {db_error}'}, status=500)


        # 5. 성공 응답 반환하기
        print(f"성공: 사용자 {user.username} 포트폴리오 DB 동기화 완료.")
        return JsonResponse({'status': 'success', 'message': '포트폴리오가 성공적으로 업데이트되었습니다.'})

    except Exception as e:
        # 요청 처리 중 예기치 않은 오류 발생
        print(f"오류: 사용자 {request.user.username if request.user.is_authenticated else '비로그인'} 포트폴리오 업데이트 처리 중 최상위 오류 발생: {e}")
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': f'서버 내부 오류가 발생했습니다: {e}'}, status=500)






User = get_user_model()

# Holding, Trade 모델 import (네 models.py에 정의되어 있어야 함)
# from .models import Holding, Trade # 보유 종목, 거래 내역 모델 import

# 임시로 모델 클래스 이름만 가정 (실제 네 모델 이름으로 변경 필요)
# class Holding: pass # 예시
# class Trade: pass # 예시

# ★★★ 중요: 실제 네 models.py에 정의된 User, Holding, Trade 모델을 정확히 임포트하고 사용해야 함 ★★★
# Holding 모델이 User와 ForeignKey로 연결되어 있고 related_name이 'holdings'라고 가정
# Trade 모델도 User와 ForeignKey로 연결되어 있고 related_name이 'trades'라고 가정
# Holding 모델에 symbol, quantity, avg_price 등의 필드가 있다고 가정
# Trade 모델에 symbol, action, quantity, price, profit, timestamp 등의 필드가 있다고 가정

@login_required # 로그인된 사용자만 이 API에 접근 가능
@require_GET   # 이 API는 GET 요청만 받음
def load_portfolio_api(request):
    """
    로그인된 사용자의 포트폴리오 상태를 DB에서 조회하여 JSON으로 반환하는 API 엔드포인트.
    """
    try:
        # 1. 현재 로그인된 사용자 객체 가져오기
        user = request.user

        print(f"로그: 사용자 {user.username}의 포트폴리오 상태 조회 요청 수신.")

        # 2. 사용자 포트폴리오 데이터 조회
        # User 모델 필드들
        # user_data = model_to_dict(user, fields=['username', 'cash', 'initial_deposit', 'level', 'user_tier', 'real_cash', 'portfolio_value'])
        # 필요한 필드만 직접 딕셔너리에 담는 것이 더 명확할 수 있습니다.

        # 2.1 User 모델의 기본 정보 가져오기
        portfolio_data = {
            'userName': user.username,
            # 필드 이름은 실제 네 User 모델의 필드 이름과 JSON 응답에서 사용할 이름에 맞춰
            'cash': user.cash, # User 모델에 cash 필드가 있다고 가정
            # 'initialDeposit': user.initial_deposit, # User 모델에 initial_deposit 필드가 있다고 가정
            'level': user.current_level, # User 모델에 level 필드가 있다고 가정
            'tier': user.user_tier, # User 모델에 user_tier 필드가 있다고 가정
            'realCash': user.real_cash, # User 모델에 real_cash 필드가 있다고 가정
            'portfolioValue': user.portfolio_value, # User 모델에 portfolio_value 필드가 있다고 가정
            # 필요에 따라 User 모델의 다른 필드들도 추가
        }

        # 2.2 보유 종목 (Holdings) 정보 가져오기
        # User 모델의 related_name='holdings'를 사용하여 보유 종목 객체들 조회
        holdings_list = []
        # user.holdings.all() -> User 모델에 related_name='holdings'로 연결된 Holding 객체들
        for holding in user.holdings.all(): # Holding 모델 객체들을 순회
            # Holding 모델 필드들을 딕셔너리로 변환하여 리스트에 추가
            # 필드 이름은 실제 네 Holding 모델 필드 이름과 JSON 응답에 맞춰
            holdings_list.append({
                # 'id': holding.id, # 클라이언트에서 Holding 객체의 DB ID가 필요하다면 추가
                'symbol': holding.symbol, # Holding 모델에 symbol 필드가 있다고 가정
                'quantity': holding.quantity, # Holding 모델에 quantity 필드가 있다고 가정
                'avgPrice': holding.avg_price, # Holding 모델에 avg_price 필드가 있다고 가정
                # 필요에 따라 Holding 모델의 다른 필드들도 추가
            })
        # 클라이언트 portfolio.holdings가 딕셔너리 형태였으므로 여기서도 딕셔너리로 구성
        # { symbol: { quantity: ..., avgPrice: ... }, ... } 형태
        holdings_dict = {h['symbol']: h for h in holdings_list} # 심볼을 키로 하는 딕셔너리 생성

        portfolio_data['holdings'] = holdings_dict


        # 2.3 거래 내역 (Trades) 정보 가져오기
        # User 모델의 related_name='trades'를 사용하여 거래 내역 객체들 조회
        trades_list = []
        # user.trades.all() -> User 모델에 related_name='trades'로 연결된 Trade 객체들
        # 최신 거래 내역부터 보여주려면 order_by('-timestamp') 등을 추가
        for trade in user.trades.all().order_by('-timestamp'): # Trade 모델 객체들을 순회 (최신순 정렬 예시)
            # Trade 모델 필드들을 딕셔너리로 변환하여 리스트에 추가
            # 필드 이름은 실제 네 Trade 모델 필드 이름과 JSON 응답에 맞춰
            trades_list.append({
                # 'id': trade.id, # 클라이언트에서 Trade 객체의 DB ID가 필요하다면 추가
                'timestamp': trade.timestamp.isoformat() if trade.timestamp else None, # 날짜/시간 형식 변환 (ISO 8601 권장)
                'symbol': trade.symbol, # Trade 모델에 symbol 필드가 있다고 가정
                'action': trade.action, # Trade 모델에 action 필드가 있다고 가정 ('buy', 'sell' 문자열)
                'quantity': trade.quantity, # Trade 모델에 quantity 필드가 있다고 가정
                'price': trade.price, # Trade 모델에 price 필드가 있다고 가정 (체결 단가)
                'profit': trade.profit if trade.action == 'sell' else None, # Trade 모델에 profit 필드가 있다면 (매도 시 손익)
                # 필요에 따라 Trade 모델의 다른 필드들도 추가
            })

        portfolio_data['trades'] = trades_list


        # 3. 포트폴리오 데이터를 JSON 응답으로 반환
        print(f"로그: 사용자 {user.username}의 포트폴리오 데이터 조회 완료. JSON 응답 반환.")
        return JsonResponse(portfolio_data)

    except Exception as e:
        # 조회 중 예기치 않은 오류 발생
        print(f"오류: 사용자 {request.user.username if request.user.is_authenticated else '비로그인'} 포트폴리오 조회 처리 중 오류 발생: {e}")
        traceback.print_exc() # 서버 로그에 자세한 오류 추적 정보 출력
        # 클라이언트에게 오류 응답 반환
        return JsonResponse({'message': '포트폴리오 데이터를 가져오는데 실패했습니다.', 'error': str(e)}, status=500)
















# --- !!! 경고: 절대 경로 사용 !!! ---
PARAMS_FILE_PATH = r"D:\AI_pycharm\pythonProject\3_AI_LLM_finance\a_korea_invest_api_env\secret_data\params.py"
# ------------------------------------

KIS_APP_KEY = None
KIS_APP_SECRET = None
# 실제 KIS API URL (실전투자 기준 - KIS 문서에서 재확인 필요)
KIS_BASE_URL = "https://openapi.koreainvestment.com:9443"

# --- 파일에서 API 키 읽어오기 ---
try:
    print(f"절대 경로에서 KIS 키 로딩 시도: {PARAMS_FILE_PATH}")
    # params.py 파일 형식 가정: 각 줄에 '변수명 = "값"' 형태
    with open(PARAMS_FILE_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("stock_API_key"):
                line = line.replace(' ', '')
                parts = line.split('key=')
                KIS_APP_KEY = parts[1].strip().strip('"').strip("'")

            elif line.startswith("stock_Secret_key"): # App Secret 변수명도 params.py에 있다고 가정
                line = line.replace(' ','')
                parts = line.split('key=')
                KIS_APP_SECRET = parts[1].strip().strip('"').strip("'")
            # 필요한 다른 키가 있다면 elif 추가

except FileNotFoundError:
    print(f"!!! 치명적 오류: 지정된 절대 경로에 params.py 파일이 없습니다: {PARAMS_FILE_PATH} !!!")
    # 이 경우 애플리케이션 실행이 불가능할 수 있음
    KIS_APP_KEY = None # None으로 설정하여 이후 함수에서 처리
    KIS_APP_SECRET = None

except Exception as e:
    print(f"!!! 치명적 오류: {PARAMS_FILE_PATH} 파일 읽기/파싱 중 예외 발생: {e} !!!")
    KIS_APP_KEY = None
    KIS_APP_SECRET = None

# --- 웹소켓 접속키 발급 함수 ---
def get_kis_approval_key():
    """KIS REST API를 호출하여 임시 웹소켓 접속키(approval_key)를 발급받습니다."""
    if not KIS_APP_KEY or not KIS_APP_SECRET:
        print("오류: KIS App Key 또는 Secret 값이 없어 approval_key를 발급할 수 없습니다.")
        return None

    path = "/oauth2/Approval"
    url = f"{KIS_BASE_URL}{path}"
    headers = {"content-type": "application/json"}
    # params.py에서 읽어온 키 사용
    body = {
        "grant_type": "client_credentials",
        "appkey": KIS_APP_KEY,
        "secretkey": KIS_APP_SECRET # KIS 문서 따라 'secretkey' 또는 'appsecret' 확인
    }
    print(f"KIS Approval Key 요청 URL: {url}")

    try:
        response = requests.post(url, headers=headers, data=json.dumps(body), timeout=10) # 타임아웃 증가
        response.raise_for_status() # 오류 시 예외 발생
        data = response.json()
        approval_key = data.get('approval_key')
        if approval_key:
            print("KIS Approval Key 발급 성공.")
            return approval_key
        else:
            print(f"오류: KIS 응답에서 'approval_key'를 찾을 수 없음: {data}")
            return None
    except requests.exceptions.Timeout:
        print(f"오류: KIS Approval API 요청 시간 초과 ({url})")
        return None
    except requests.exceptions.RequestException as e:
        print(f"오류: KIS Approval API 요청 실패: {e}")
        if e.response is not None:
            print(f"응답 코드: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"오류 응답 내용 (JSON): {error_data}")
            except json.JSONDecodeError:
                print(f"오류 응답 내용 (Text): {e.response.text}")
        return None
    except json.JSONDecodeError as e:
         print(f"오류: KIS Approval API JSON 응답 파싱 실패: {e}")
         print(f"수신된 응답 내용: {response.text}")
         return None


@login_required # 로그인 사용자만 키 발급 가능하도록
def get_websocket_key_api(request): # ★ 키 발급 전용 API 뷰 ★
    """ KIS 웹소켓 접속 승인키를 발급하여 JSON으로 반환하는 API 뷰 """
    print("[API] 웹소켓 승인키 발급 요청 받음 (/api/get_websocket_key/)")
    approval_key = get_kis_approval_key() # 별도 파일의 함수 호출

    if approval_key:
        # 성공 시
        print("[API] 웹소켓 승인키 발급 성공")
        return JsonResponse({'success': True, 'approval_key': approval_key})
    else:
        # 실패 시
        print("[API] 웹소켓 승인키 발급 실패")
        return JsonResponse({'success': False, 'message': '웹소켓 승인키 발급에 실패했습니다.'}, status=500) # 500 서버 오류





























@login_required # 로그인 필수
@require_POST  # POST 요청만 허용
# @ensure_csrf_cookie # CSRF 쿠키 보장 (필요에 따라)
def process_trade_result_api_view(request):
    """ JavaScript로부터 매도 결과를 받아 서비스 함수를 호출하는 API 뷰 """
    # 뷰 함수에 @transaction.atomic을 적용하면 이 함수 내부에서 호출하는 모든 DB 작업이 하나의 트랜잭션으로 묶임
    # process_trade_result 내부의 grant_asi_reward도 이 트랜잭션에 포함됨.
    # grant_asi_reward 자체에 @transaction.atomic이 있어도 중첩 트랜잭션으로 잘 동작함.
    try:
        # 요청 본문(body)에서 JSON 데이터 읽기
        data = json.loads(request.body)
        profit_usd = data.get('profit') # JavaScript에서 보낸 'profit' 키의 값
        user_id = request.user.id

        # profit 값이 숫자인지 확인 (간단한 유효성 검사)
        # isinstance(profit_usd, (int, float, str)) 로 더 유연하게 받을 수도 있음
        if profit_usd is None or not isinstance(profit_usd, (int, float, str)): # 숫자나 문자열 형태의 숫자를 허용
            return JsonResponse({'success': False, 'message': '유효한 수익 정보(profit)가 필요합니다.'}, status=400)

        # service 함수 호출하여 DB 업데이트 시도
        # process_trade_result 함수는 이제 (처리 성공 여부, 지급된 ASI 금액(Decimal))을 반환
        # profit_usd가 문자열일 경우 float으로 변환해서 전달
        success, granted_asi_amount = process_trade_result(user_id, float(profit_usd)) # float으로 변환해서 전달

        if success:
            # 성공 시, 응답에 지급된 ASI 금액 포함
            # Decimal 타입은 JsonResponse가 처리 못하므로 문자열이나 float으로 변환
            # granted_asi_amount는 Decimal("0.0") 일 수 있으므로 float 변환 안전
            return JsonResponse({
                'success': True,
                'message': '매도 결과가 처리되었습니다.',
                'asi_reward': float(granted_asi_amount) # Decimal을 float으로 변환하여 응답
            })
        else:
            # 서비스 함수 내부에서 실패한 경우
            # process_trade_result 함수 내부의 print 로그로 원인 파악 필요
            # 실패 시 보상 금액은 0이므로 포함하지 않거나 0으로 포함
             return JsonResponse({'success': False, 'message': '매도 결과 처리 중 서버 내부 오류가 발생했습니다.'}, status=500)


    except json.JSONDecodeError:
        # 요청 본문이 유효한 JSON이 아닐 경우
        return JsonResponse({'success': False, 'message': '잘못된 요청 형식입니다 (JSON 오류).'}, status=400)
    except Exception as e:
        # 기타 예외 처리 (로그인 안 된 경우 등 @login_required 데코레이터에서 처리되지만, 안전상)
        print(f"API 오류: /api/trade/process_result/ - {e}") # 서버 로그에 기록
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': '서버 내부 오류가 발생했습니다.'}, status=500)









@login_required # 로그인 필수
@require_POST  # POST 요청만 허용
# @csrf_exempt # CSRF 테스트 필요 시 임시 사용, 실제로는 JS에서 토큰 전송 필요
def initiate_withdrawal_api_view(request):
    """ 사용자의 ASI Coin 온체인 출금 요청을 처리하는 API 뷰 """
    try:
        # 1. 요청 데이터 파싱
        data = json.loads(request.body)
        # JavaScript에서 'amount' 키로 출금 금액(문자열 또는 숫자)을 보냈다고 가정
        amount_str = data.get('amount')
        user_id = request.user.id

        # 2. 입력값 유효성 검증
        if amount_str is None:
            return JsonResponse({'success': False, 'message': '출금할 금액(amount)이 요청에 포함되지 않았습니다.'}, status=400)

        try:
            amount_to_withdraw = Decimal(amount_str)
            if amount_to_withdraw <= 0:
                raise ValueError("출금 금액은 0보다 커야 합니다.")
        except (ValueError, InvalidOperation):
             return JsonResponse({'success': False, 'message': '출금 금액이 올바른 숫자 형식이 아닙니다.'}, status=400)

        # 3. 핵심 서비스 함수 호출
        # initiate_onchain_withdrawal 함수는 {'success': True/False, 'tx_hash': '...', 'message': '...'} 형태의 dict를 반환한다고 가정
        result = initiate_onchain_withdrawal(user_id, amount_to_withdraw)

        # 4. 서비스 함수 결과에 따라 최종 응답 반환
        if result.get('success'):
            # 성공 시 (tx_hash 포함)
            return JsonResponse(result)
        else:
            # 실패 시 (message 포함)
            # 실패 원인(잔액 부족, 주소 미등록 등)에 따라 status code를 다르게 주는 것이 좋음 (여기서는 400으로 통일)
            return JsonResponse(result, status=400)

    except json.JSONDecodeError:
        # 요청 본문이 JSON이 아닐 경우
        return JsonResponse({'success': False, 'message': '잘못된 요청 형식입니다 (JSON 오류).'}, status=400)
    except Exception as e:
        # 기타 예상치 못한 서버 오류
        print(f"API 오류: /api/wallet/withdraw/ - {e}") # 서버 로그에 기록
        return JsonResponse({'success': False, 'message': '서버 내부 오류가 발생했습니다.'}, status=500)


@login_required
def profile_settings_view(request):
    user = request.user
    # GET 요청 시 또는 다른 폼 제출 시 보여줄 초기 폼 인스턴스
    # initial 값을 명시적으로 전달하면 changed_data 비교에 사용됩니다.
    nickname_form_instance = NicknameChangeForm(instance=user, initial={'nickname': user.nickname}, user_instance=user)
    position_sharing_form_instance = PositionSharingForm(instance=user)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        print(f"[PROFILE_SETTINGS] POST 요청 받음, form_type: {form_type}")

        if form_type == 'nickname':
            if not user.can_change_nickname():  # 이 시점의 user.nickname은 DB의 현재 값
                messages.error(request, _("닉네임 변경 주기가 아직 지나지 않았습니다."))
                return redirect('profile_settings')

            # POST 데이터와 함께 instance를 전달하여 어떤 객체를 업데이트할지 알려줍니다.
            # initial도 함께 전달하면 changed_data가 더 정확하게 작동합니다.
            nickname_form_instance = NicknameChangeForm(request.POST, instance=user,
                                                        initial={'nickname': user.nickname}, user_instance=user)

            if nickname_form_instance.is_valid():
                print("[PROFILE_SETTINGS] NicknameChangeForm 유효성 검사 통과!")

                # form.changed_data는 초기값(instance의 값)과 비교하여 변경된 필드 이름들의 리스트를 반환합니다.
                if 'nickname' in nickname_form_instance.changed_data:
                    print(
                        f"[PROFILE_SETTINGS] 닉네임이 실제로 변경됨 (form.changed_data 확인). 새 닉네임: '{nickname_form_instance.cleaned_data.get('nickname')}'")

                    # 폼의 save() 메서드가 instance의 nickname을 cleaned_data 값으로 업데이트하고 저장 준비를 합니다.
                    # NicknameChangeForm의 save 메서드는 ModelForm의 기본 save를 사용합니다.
                    updated_user = nickname_form_instance.save(commit=False)  # DB에 바로 저장 X, nickname 필드는 업데이트됨
                    updated_user.nickname_last_updated = timezone.now()
                    updated_user.save(update_fields=['nickname', 'nickname_last_updated'])  # 변경된 nickname과 시간만 저장

                    messages.success(request, _("닉네임이 성공적으로 변경되었습니다."))
                else:
                    # 폼은 유효하지만, 닉네임 필드 값 자체는 초기값과 동일한 경우
                    print(
                        f"[PROFILE_SETTINGS] 닉네임이 변경되지 않음 (form.changed_data에 'nickname' 없음). 제출된 값: '{nickname_form_instance.cleaned_data.get('nickname')}'")
                    messages.info(request, _("기존과 동일한 닉네임이거나 입력된 내용이 없습니다. 변경사항이 없습니다."))
                return redirect('profile_settings')
            else:
                # 폼 유효성 검사 실패 (예: 금칙어, 다른 사용자가 이미 사용하는 새 닉네임 등)
                print(
                    f"[PROFILE_SETTINGS] NicknameChangeForm 유효성 검사 실패! 오류: {nickname_form_instance.errors.as_json(escape_html=True)}")
                messages.error(request, _("닉네임 변경에 실패했습니다. 입력값을 확인해주세요."))
                # 오류가 있는 nickname_form_instance가 아래 context에 포함되어 다시 렌더링됨

        elif form_type == 'sharing':
            position_sharing_form_instance = PositionSharingForm(request.POST, instance=user)
            if position_sharing_form_instance.is_valid():
                position_sharing_form_instance.save()  # ModelForm의 save는 instance를 업데이트하고 저장함
                messages.success(request, _("포지션 공개 설정이 저장되었습니다."))
                return redirect('profile_settings')
            else:
                messages.error(request, _("포지션 공개 설정 저장에 실패했습니다."))
                # 오류가 있는 position_sharing_form_instance가 아래 context에 포함됨

    # GET 요청이거나, POST 처리 후 오류가 있어서 다시 렌더링해야 하는 경우
    # nickname_form_instance와 position_sharing_form_instance는
    # GET 요청 시에는 위에서 초기화된 깨끗한 폼 인스턴스,
    # POST 오류 시에는 request.POST 데이터와 오류 정보가 담긴 폼 인스턴스가 됩니다.

    nickname_change_cooldown_time_left_str = ""
    # User 모델에 can_change_nickname 메서드가 정의되어 있다고 가정
    if hasattr(user, 'can_change_nickname') and user.nickname_last_updated and not user.can_change_nickname():
        cooldown_duration = timedelta(minutes=5)  # 폼 또는 모델에 정의된 쿨타임과 일치해야 함
        cooldown_end_time = user.nickname_last_updated + cooldown_duration
        time_left = cooldown_end_time - timezone.now()
        if time_left.total_seconds() > 0:
            minutes_left = int(time_left.total_seconds() // 60)
            seconds_left = int(time_left.total_seconds() % 60)
            if minutes_left > 0:
                nickname_change_cooldown_time_left_str += f"{minutes_left}분 "
            nickname_change_cooldown_time_left_str += f"{seconds_left}초"

    context = {
        'nickname_form': nickname_form_instance,
        'position_sharing_form': position_sharing_form_instance,
        'user': user,
        'nickname_change_cooldown_time_left': nickname_change_cooldown_time_left_str
    }
    return render(request, 'main/user_profile_setting.html', context)


@login_required
def account_delete_view(request):
    if request.method == 'POST':
        user = request.user

        # 사용자 비활성화 및 관련 정보 업데이트
        user.is_active = False
        user.date_deactivated = timezone.now()
        user.can_rejoin_at = timezone.now() + timedelta(days=30)  # 30일 후 재가입 가능
        # 필요하다면 이메일, 닉네임 등에 고유한 비활성 접미사 추가 (예: user_deactivated_123)
        # user.email = f"{user.email}.deleted.{user.id}" # 예시
        # user.username = f"{user.username}_deleted_{user.id}" # 예시 (만약 username을 재사용하지 않도록 한다면)
        user.save()

        logout(request)  # 사용자 로그아웃
        messages.success(request, _("회원 탈퇴가 정상적으로 처리되었습니다. 이용해주셔서 감사합니다."))
        return redirect('index')  # 홈페이지로 리디렉션

    # GET 요청 시 (또는 POST가 아닐 시) 프로필 설정 페이지로 리디렉션 (또는 별도 확인 페이지)
    return redirect('user_profile_settings')











User = get_user_model()



@login_required # 시뮬레이터 페이지는 로그인 필수 가정
def index2_simulator_page_backup(request): # ★ 시뮬레이터 HTML 페이지 렌더링 전용 뷰 ★
    """ 시뮬레이터 HTML 페이지만 렌더링하는 뷰 """
    print("시뮬레이터 페이지 요청 받음 (/index2_simulator/)")
    context = {
        'user': request.user,
    }
    # 템플릿 파일 경로는 실제 프로젝트 구조에 맞게 확인 필요
    return render(request, 'main/index2_simulator.html', context)