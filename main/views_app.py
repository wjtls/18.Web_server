# 앱에서 사용되는 api

# main/views_app.py

import json
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as django_login  # login 함수 이름 충돌 방지
from django.views.decorators.csrf import csrf_exempt  # API 테스트를 위해 임시로 CSRF 비활성화 (운영 시에는 다른 방식 권장)
from django.views.decorators.http import require_POST
from django.db import IntegrityError
from django.contrib.auth import get_user_model
User = get_user_model()

@csrf_exempt  # << API 테스트를 위해 임시로 추가 (실제 운영 시에는 토큰 인증 등으로 대체)
@require_POST  # 이 API는 POST 요청만 받도록 설정
def app_login_api(request):
    print('로그인 api 가동')
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'success': False, 'message': '아이디와 비밀번호를 모두 입력해주세요.'}, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Django 세션에 로그인 (선택 사항, 앱에서는 주로 토큰 사용)
            # django_login(request, user)

            # 앱에 반환할 사용자 정보 (필요에 따라 추가/제외)
            user_data = {
                'username': user.username,
                'email': user.email,
                'nickname': getattr(user, 'nickname', user.username),  # User 모델에 nickname 필드가 있다면
                # 'user_id': user.id, # 필요하다면 사용자 ID
                # ... 기타 필요한 최소한의 정보 ...
            }
            # TODO: 실제 운영 시에는 여기서 JWT 같은 인증 토큰을 생성하여 함께 반환해야 합니다.
            # 지금은 간단히 성공 여부와 사용자 정보만 반환합니다.
            return JsonResponse({'success': True, 'message': '로그인 성공!', 'user': user_data})
        else:
            return JsonResponse({'success': False, 'message': '아이디 또는 비밀번호가 올바르지 않습니다.'}, status=401)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '잘못된 요청 형식입니다.'}, status=400)
    except Exception as e:
        # 실제 운영 환경에서는 로깅 등으로 오류를 기록하는 것이 좋습니다.
        return JsonResponse({'success': False, 'message': f'서버 오류가 발생했습니다: {str(e)}'}, status=500)



#로그인
@csrf_exempt  # << API 테스트를 위해 임시로 추가
@require_POST  # 이 API는 POST 요청만 받도록 설정
def app_register_api(request):
    print('회원가입 api 가동')
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')  # 앱에서 이메일도 받는다고 가정
        nickname = data.get('nickname')
        phone_number = data.get('phone_number')  # 선택 사항
        # full_name = data.get('full_name') # 선택 사항
        # terms_accepted = data.get('terms_accepted') # 약관 동의 여부

        # --- 필수 값 검증 ---
        if not all([username, password, email, nickname]):  # 예시: username, password, email, nickname 필수
            missing_fields = []
            if not username: missing_fields.append('아이디')
            if not password: missing_fields.append('비밀번호')
            if not email: missing_fields.append('이메일')
            if not nickname: missing_fields.append('닉네임')
            return JsonResponse({'success': False, 'message': f'{", ".join(missing_fields)} 항목을 모두 입력해주세요.'},
                                status=400)

        # --- 사용자 생성 ---
        # 아이디(username) 중복 확인
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': '이미 사용 중인 아이디입니다.'}, status=400)

        # 이메일 중복 확인
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': '이미 등록된 이메일입니다.'}, status=400)

        # 닉네임 중복 확인
        if User.objects.filter(nickname=nickname).exists():
            return JsonResponse({'success': False, 'message': '이미 사용 중인 닉네임입니다.'}, status=400)

        # 비밀번호 길이 등 유효성 검사 (Django User 모델 기본 검증 외 추가 필요시)
        if len(password) < 8:  # 예시: 최소 8자
            return JsonResponse({'success': False, 'message': '비밀번호는 8자 이상이어야 합니다.'}, status=400)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            nickname=nickname,
            phone_number=phone_number,  # User 모델에 해당 필드가 있어야 함
            # full_name=full_name, # User 모델에 해당 필드가 있어야 함
            # phone_verified=True, # OTP 인증 등을 거쳤다면 True로 설정
        )

        # 회원가입 성공 후 바로 로그인 처리 (선택 사항)
        # django_login(request, user) # 세션 기반 로그인

        # 앱에 반환할 사용자 정보
        user_data = {
            'username': user.username,
            'email': user.email,
            'nickname': user.nickname,
        }
        # TODO: 실제 운영 시에는 여기서도 인증 토큰을 생성하여 함께 반환하는 것이 좋습니다.
        return JsonResponse({'success': True, 'message': '회원가입 성공! 로그인해주세요.', 'user': user_data}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '잘못된 요청 형식입니다.'}, status=400)
    except IntegrityError as e:  # 주로 unique 제약 조건 위반 시 발생
        print(f"회원가입 IntegrityError: {e}")
        # 좀 더 구체적인 오류 메시지 분기 가능
        if 'username' in str(e).lower():
            return JsonResponse({'success': False, 'message': '이미 사용 중인 아이디입니다. (DB오류)'}, status=400)
        if 'email' in str(e).lower():
            return JsonResponse({'success': False, 'message': '이미 등록된 이메일입니다. (DB오류)'}, status=400)
        if 'nickname' in str(e).lower():
            return JsonResponse({'success': False, 'message': '이미 사용 중인 닉네임입니다. (DB오류)'}, status=400)
        return JsonResponse({'success': False, 'message': '사용자 정보 등록 중 오류가 발생했습니다. (중복된 값일 수 있음)'}, status=400)
    except Exception as e:
        print(f"회원가입 Exception: {e}")  # 서버 로그에 상세 오류 기록
        return JsonResponse({'success': False, 'message': f'서버 오류가 발생했습니다: {str(e)}'}, status=500)


from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication # Simple JWT 사용 시


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def app_load_portfolio_api(request):
    user = request.user
    print(f"로그: 사용자 {user.username}의 포트폴리오 상태 조회 요청 수신 (DRF 인증).")

    try:
        holdings_from_db = user.holdings.all()  # type: ignore

        # stock_value_calc는 Holding 모델의 current_value 속성을 사용하므로,
        # 해당 속성이 레버리지를 이미 반영하고 있어야 함 (이전 단계에서 Holding 모델 수정 완료)
        stock_value_calc = sum(
            h.current_value for h in holdings_from_db if h.current_value is not None
        )

        # User 모델에 portfolio_value 필드가 없다면 직접 계산
        # 여기서는 user.cash와 위에서 계산한 stock_value_calc를 합산
        # total_value_calc = user.cash + stock_value_calc # Decimal로 계산하는 것이 더 정확할 수 있음
        # 또는 user.portfolio_value를 신뢰할 수 있다면 그대로 사용
        total_value_calc = getattr(user, 'portfolio_value', float(user.cash) + float(stock_value_calc))

        # deposit 필드가 User 모델에 없다면, 초기 자본금 계산 방식을 명확히 해야 함.
        # 프론트엔드에서는 100,000을 기준으로 계산하므로, 여기 deposit도 그에 맞추거나,
        # 프론트엔드가 사용하는 deposit과 다른 의미라면 명확히 구분해야 함.
        # 여기서는 User 모델에 deposit 필드가 있다고 가정. 없다면 user.initial_capital 등 다른 필드 사용.
        initial_deposit_calc = getattr(user, 'deposit', 10000000)  # 기본값은 initialPortfolioData와 일치시킴

        total_pl_calc = float(total_value_calc) - float(initial_deposit_calc)  # float으로 형변환하여 계산
        total_return_calc = (total_pl_calc / float(initial_deposit_calc)) * 100 if initial_deposit_calc else 0

        returns_chart_data_example = {
            'dataSets': [{
                'values': [{'y': 0}, {'y': 1.2}, {'y': -0.5}, {'y': 2.5}],
                'label': '수익률 (%)',
            }]
        }

        portfolio_summary = {
            'username': user.nickname or user.username,  # type: ignore
            'totalValue': total_value_calc,
            'stockValue': stock_value_calc,
            'cash': user.cash,  # type: ignore
            'deposit': initial_deposit_calc,
            'totalPl': total_pl_calc,
            'totalReturn': total_return_calc,
            'returnsChartData': returns_chart_data_example,
            'level': user.current_level if hasattr(user, 'current_level') else 1,  # type: ignore
            'tierName': user.get_tier_info()['name'] if hasattr(user, 'get_tier_info') else 'Bronze',  # type: ignore
            'tierImage': user.get_tier_info()['image'] if hasattr(user, 'get_tier_info') else None,  # type: ignore
        }


        holdings_list = []
        for holding in holdings_from_db:
            holdings_list.append({
                'symbol': holding.symbol,
                'name': holding.symbol,
                'quantity': holding.quantity,
                'avgPrice': holding.avg_price,
                'currentPrice': holding.current_price,  # Holding 모델의 @property
                'currentValue': holding.current_value,  # Holding 모델의 @property (레버리지 반영)
                'profitLoss': holding.profit_loss,  # Holding 모델의 @property (레버리지 반영)
                'returnPercentage': holding.return_percentage,  # Holding 모델의 @property (레버리지 반영)
                'leverage': holding.leverage,  # <<< 추가: 홀딩 객체의 레버리지 값
                'exchange_code': getattr(holding, 'exchange_code', None),  # Holding 모델에 exchange_code 필드가 있다면
                'assetType': getattr(holding, 'assetType', ('coin' if 'USDT' in holding.symbol else 'stock')),
                # assetType 추론
            })

        trades_list = []
        # user.trades 는 related_name='trades'로 정의되어 있어야 함
        recent_trades = user.trades.all().order_by('-timestamp')[:50] if hasattr(user, 'trades') else []  # type: ignore
        for trade in recent_trades:
            trades_list.append({
                'id': trade.pk,
                'timestamp': trade.timestamp.isoformat() if trade.timestamp else None,
                'symbol': trade.symbol,
                'name': trade.symbol,
                'action': trade.action,
                'type': trade.action,
                'quantity': trade.quantity,
                'price': trade.price,
                'amount': trade.quantity * trade.price,
                'profit': trade.profit if trade.action == 'sell' else None,
                'leverage': trade.leverage,  # <<< 추가: 거래 객체의 레버리지 값
                'commission': trade.commission,  # <<< 추가: 거래 객체의 수수료 값
                'assetType': getattr(trade, 'assetType', ('coin' if 'USDT' in trade.symbol else 'stock')),
                # assetType 추론
            })

        response_data = {
            'success': True,
            'portfolio': portfolio_summary,
            'holdings': holdings_list,
            'trades': trades_list
        }
        # DRF를 사용하고 있으므로 Response 객체 사용 권장
        # from rest_framework.response import Response
        return Response(response_data)  # JsonResponse 대신 DRF의 Response 사용

    except Exception as e:
        print(f"오류: 사용자 {user.username} 포트폴리오 조회 중 오류: {e}")  # type: ignore
        traceback.print_exc()
        # DRF 사용 시
        # from rest_framework import status
        return Response({'success': False, 'message': '포트폴리오 데이터를 가져오는데 실패했습니다.', 'error': str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # return JsonResponse({'success': False, 'message': '포트폴리오 데이터를 가져오는데 실패했습니다.', 'error': str(e)}, status=500)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP  # ROUND_HALF_UP는 필요시 사용
import time
from datetime import datetime

from django.db import transaction
# from django.db.models import F, Sum # Sum은 직접 사용하지 않으므로 제거 가능

# settings.AUTH_USER_MODEL 대신 실제 User 모델을 가져오는 것이 더 명확할 수 있습니다.
# from django.contrib.auth import get_user_model
# User = get_user_model()
# 여기서는 제공된 코드를 따라 .models 에서 가져옵니다.
from .models import User, Holding, Trade
from chart.blockchain_reward import process_trade_result

# --- 거래 관련 설정값 ---
TRANSACTION_FEE_RATE = Decimal('0.0025')
SLIPPAGE_PERCENT_BUY = Decimal('0.1')
SLIPPAGE_PERCENT_SELL = Decimal('0.1')


class AppTradeProcessAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = request.user
        payload = request.data

        symbol = payload.get('symbol')
        action = payload.get('action')
        # exchange = payload.get('exchange') # 필요시 사용

        try:
            quantity_str = payload.get('quantity')
            price_str = payload.get('price')
            leverage_str = payload.get('leverage', '1')  # 기본값 1

            if quantity_str is None or price_str is None:
                return Response({'success': False, 'message': '수량 또는 가격 정보가 누락되었습니다.'},
                                status=status.HTTP_400_BAD_REQUEST)

            quantity = Decimal(quantity_str)
            order_price = Decimal(price_str)
            leverage = int(leverage_str)  # 레버리지는 정수로 처리

            if not (1 <= leverage <= 20):  # 레버리지 범위 검사
                return Response({'success': False, 'message': '레버리지는 1에서 20 사이여야 합니다.'},
                                status=status.HTTP_400_BAD_REQUEST)

            if quantity <= Decimal('0') or order_price <= Decimal('0'):
                return Response({'success': False, 'message': '수량과 가격은 0보다 커야 합니다.'},
                                status=status.HTTP_400_BAD_REQUEST)

        except InvalidOperation:
            return Response({'success': False, 'message': '수량, 가격, 레버리지 값에 숫자 형식이 아닌 값이 포함되어 있습니다.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except ValueError:  # int(leverage_str) 변환 오류 등
            return Response({'success': False, 'message': '레버리지 값은 정수여야 합니다.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success': False, 'message': f'입력 값 처리 오류: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        executed_price = order_price
        if action == 'buy':
            slippage_amount = order_price * (SLIPPAGE_PERCENT_BUY / Decimal('100'))
            executed_price = order_price + slippage_amount
        elif action == 'sell':
            slippage_amount = order_price * (SLIPPAGE_PERCENT_SELL / Decimal('100'))
            executed_price = order_price - slippage_amount

        # executed_price = executed_price.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP) # 필요시 가격 정밀도 조정

        trade_value_before_fees = executed_price * quantity
        commission = trade_value_before_fees * TRANSACTION_FEE_RATE
        # commission = commission.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP) # 필요시 수수료 정밀도 조정

        realized_profit_loss = Decimal('0')  # 이번 매도로 발생하는 실현손익 (레버리지, 수수료 미반영 매매차익)

        try:
            user_locked = User.objects.select_for_update().get(pk=request.user.pk)
            user_cash_before_trade = Decimal(str(user_locked.cash))

            # Holding 조회/생성 시 leverage 사용
            holding, created = Holding.objects.select_for_update().get_or_create(
                user=user_locked,
                symbol=symbol,
                leverage=leverage,  # leverage 조건 추가
                defaults={'quantity': Decimal('0'), 'avg_price': Decimal('0')}
            )
            # DB에서 float으로 저장된 값을 Decimal로 변환하여 사용
            holding_quantity_before_trade = Decimal(str(holding.quantity))
            holding_avg_price_before_trade = Decimal(str(holding.avg_price))

            if action == 'buy':
                # 레버리지 거래 시 실제 필요한 증거금은 (총 거래대금 / 레버리지) + 수수료.
                # 하지만 현재 시스템은 총 거래대금 전체를 현금으로 지불하고, 레버리지는 손익에만 배수로 적용하는 방식인 것으로 보임.
                # 따라서 현금 차감 로직은 기존과 유사하게 유지 (총 거래대금 + 수수료)
                total_cost = trade_value_before_fees + commission
                if user_cash_before_trade < total_cost:
                    return Response({'success': False, 'message': '현금이 부족합니다 (수수료 포함).'},
                                    status=status.HTTP_400_BAD_REQUEST)

                user_locked.cash = float(user_cash_before_trade - total_cost)

                # 평균 단가 계산 로직은 레버리지와 관계없이 기초 자산 기준으로 동일
                current_total_value_of_holding = holding_avg_price_before_trade * holding_quantity_before_trade
                new_total_quantity = holding_quantity_before_trade + quantity

                if new_total_quantity > Decimal('0'):
                    new_avg_price = (current_total_value_of_holding + trade_value_before_fees) / new_total_quantity
                    holding.avg_price = float(new_avg_price)
                else:  # 이 경우는 사실상 발생하기 어려움 (매수인데 수량이 0이 되는 경우)
                    holding.avg_price = float(executed_price)

                holding.quantity = float(new_total_quantity)
                # holding.leverage = leverage # get_or_create에서 이미 설정됨 또는 기존 값 유지

            elif action == 'sell':
                if holding_quantity_before_trade < quantity:
                    return Response({'success': False, 'message': f'{symbol} ({leverage}x) 보유 수량이 부족합니다.'},
                                    status=status.HTTP_400_BAD_REQUEST)

                net_proceeds = trade_value_before_fees - commission

                # 실현 손익 계산 시 레버리지 적용
                price_difference = executed_price - holding_avg_price_before_trade
                unleveraged_profit_on_sold_units = price_difference * quantity
                realized_profit_loss = unleveraged_profit_on_sold_units * Decimal(
                    str(holding.leverage))  # holding.leverage 사용

                user_locked.cash = float(user_cash_before_trade + net_proceeds)
                holding.quantity = float(holding_quantity_before_trade - quantity)

                # 모든 수량을 매도하여 잔고가 0이 되면 평단가는 의미가 없어지므로 0으로 설정하거나, 레코드 삭제 고려
                if holding.quantity == 0.0:
                    holding.avg_price = 0.0

            else:
                return Response({'success': False, 'message': '잘못된 거래 유형입니다.'}, status=status.HTTP_400_BAD_REQUEST)

            user_locked.save(update_fields=['cash'])

            if holding.quantity == Decimal('0') and not created:  # Decimal 비교로 변경
                holding.delete()
                print(f"[DB업데이트] {user_locked.username} - {symbol} ({leverage}x) 보유 수량 0 되어 삭제됨.")
            else:
                holding.save()

            # 포트폴리오 가치 업데이트 (Holding 모델의 current_value 속성이 레버리지를 반영하므로, sum은 그대로 사용 가능)
            all_holdings_after_trade = Holding.objects.filter(user=user_locked)
            current_total_stock_value = Decimal('0')
            for h_item in all_holdings_after_trade:
                # h_item.current_value는 Holding 모델의 @property로 계산된 값 (레버리지 반영됨)
                current_total_stock_value += Decimal(str(h_item.current_value))

            user_locked.portfolio_value = float(Decimal(str(user_locked.cash)) + current_total_stock_value)
            # user_locked.save() # 아래에서 한번에 저장하거나, cash와 portfolio_value 함께 저장
            user_locked.save(update_fields=['portfolio_value'])  # cash는 위에서 저장, 여기서는 portfolio_value만

            # 거래 내역 기록
            new_trade = Trade.objects.create(
                user=user_locked,
                symbol=symbol,
                action=action,
                quantity=float(quantity),
                price=float(executed_price),
                profit=float(realized_profit_loss) if action == 'sell' else None,  # 레버리지 적용된 실현손익
                leverage=leverage,  # Trade 모델에 leverage 필드가 있다고 가정
                commission=float(commission)  # Trade 모델에 commission 필드가 있다고 가정
            )
            print(f"[DB업데이트] 거래 내역 기록 완료: {new_trade.id}")

        except Holding.DoesNotExist:  # get_or_create 실패 시 (이론상 발생 안 함)
            return Response({'success': False, 'message': '보유 종목 정보를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as db_error:
            import traceback
            traceback.print_exc()
            return Response({'success': False, 'message': f'거래 처리 중 DB 오류: {str(db_error)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 보상 처리 (매도 시 realized_profit_loss 사용)
        profit_for_reward_float = float(realized_profit_loss)  # action == 'sell' 일 때만 의미있는 값

        try:
            success_reward, granted_asi_amount_decimal = process_trade_result(user_locked.id, profit_for_reward_float)
            response_payload = {
                'success': True,
                'message': '거래 및 보상 처리가 완료되었습니다.',
                'executed_price': float(executed_price),
                'profit_loss': float(realized_profit_loss) if action == 'sell' else None,
                'commission_paid': float(commission),
                'asi_reward': float(granted_asi_amount_decimal) if success_reward else 0.0,
                # 'xp_reward': ??, # XP 보상 로직 추가 필요시
                'trade_id': new_trade.id,  # 생성된 Trade 객체의 ID 사용
                'timestamp': new_trade.timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'  # Trade 객체의 타임스탬프 사용
            }
            if not success_reward:
                response_payload['message'] = '거래는 처리되었으나, 보상 조건에 해당하지 않습니다.'

            return Response(response_payload, status=status.HTTP_200_OK)

        except Exception as reward_error:
            import traceback
            traceback.print_exc()
            # 거래 자체는 성공했으므로, 거래 정보는 그대로 반환하되 보상 실패 메시지 추가
            return Response({
                'success': True,  # 거래는 성공했음을 의미
                'message': '거래는 처리되었으나, 보상 처리 중 오류가 발생했습니다.',
                'executed_price': float(executed_price),
                'profit_loss': float(realized_profit_loss) if action == 'sell' else None,
                'commission_paid': float(commission),
                'asi_reward': 0.0,  # 보상 실패 시 0
                'trade_id': new_trade.id,
                'timestamp': new_trade.timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
                'reward_error_details': str(reward_error)
            }, status=status.HTTP_200_OK)  # 또는 status.HTTP_207_MULTI_STATUS