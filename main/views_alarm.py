from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import UserDevice, AlarmSubscription
from .serializers import AlarmSubscriptionSerializer  # Serializer는 직접 만들어야 함


class RegisterDeviceAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        fcm_token = request.data.get('fcm_token')
        if not fcm_token:
            return Response({'error': 'FCM token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # 기존에 있으면 업데이트, 없으면 생성
        UserDevice.objects.update_or_create(user=request.user, defaults={'fcm_token': fcm_token})
        return Response({'success': 'Device registered successfully.'}, status=status.HTTP_200_OK)


class AlarmSettingsAPI(APIView):  #알람 토글 켜면 DB에 AlarmSubscription 정보 저장
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscriptions = AlarmSubscription.objects.filter(user=request.user)
        # 간단한 dict 형태로 반환
        settings = {sub.trader_id: sub.is_active for sub in subscriptions}
        return Response(settings)

    def post(self, request):
        trader_id = request.data.get('trader_id')
        is_active = request.data.get('is_active')

        if trader_id is None or is_active is None:
            return Response({'error': 'trader_id and is_active are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        plan = user.subscription_plan

        # 구독 플랜에 따른 권한 체크
        if trader_id != 'trader1' and plan == 'BASIC':
            return Response({'error': '베이직 플랜은 Trader 1 알람만 설정할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)
        if plan == 'FREE':
            return Response({'error': '무료 사용자는 알람을 설정할 수 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

        subscription, created = AlarmSubscription.objects.update_or_create(
            user=user,
            trader_id=trader_id,
            defaults={'is_active': is_active}
        )
        return Response({'trader_id': trader_id, 'is_active': subscription.is_active}, status=status.HTTP_200_OK)

class QuizAlarmSettingsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ 현재 사용자의 퀴즈 알람 설정 상태를 반환합니다. """
        return Response({'quiz_alarm_enabled': request.user.quiz_alarm_enabled})

    def post(self, request):
        """ 사용자의 퀴즈 알람 설정을 변경합니다. """
        is_active = request.data.get('is_active')
        if not isinstance(is_active, bool):
            return Response({'error': 'is_active (boolean) is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user.quiz_alarm_enabled = is_active
        user.save(update_fields=['quiz_alarm_enabled'])
        return Response({'success': True, 'quiz_alarm_enabled': is_active})