# main/serializers.py

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils import timezone  # timezone import 추가

User = get_user_model()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        # token['nickname'] = getattr(user, 'nickname', user.username) # 예시
        return token

    def validate(self, attrs):
        data = super().validate(attrs)  # 이 호출은 이미 access, refresh 토큰을 data 딕셔너리에 포함시킵니다.

        # self.user는 인증된 사용자 객체입니다.
        # MyPageScreen.js에서 필요한 모든 정보를 여기에 추가합니다.

        # get_tier_info()와 get_subscription_plan_display()는 User 모델의 메서드라고 가정합니다.
        # 만약 없다면, 해당 로직을 여기서 직접 구현하거나 User 모델에 추가해야 합니다.
        tier_info_data = None
        if hasattr(self.user, 'get_tier_info'):
            tier_info_data = self.user.get_tier_info()

        subscription_plan_display_val = None
        if hasattr(self.user, 'get_subscription_plan_display'):
            subscription_plan_display_val = self.user.get_subscription_plan_display()
        else:
            subscription_plan_display_val = getattr(self.user, 'subscription_plan', 'FREE')

        # current_subscription_end_date 처리
        # User 모델에 이 필드가 없다면, 관련 모델에서 가져오거나 None/기본값 사용
        current_subscription_end_date_val = getattr(self.user, 'current_subscription_end_date', None)
        # DateTimeField를 ISO 문자열로 직렬화 (DRF가 기본적으로 처리해 줄 수 있지만, 명시적으로 할 수도 있음)
        if current_subscription_end_date_val and hasattr(current_subscription_end_date_val, 'isoformat'):
            current_subscription_end_date_val = current_subscription_end_date_val.isoformat()

        user_data = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'nickname': getattr(self.user, 'nickname', self.user.username),
            'full_name': getattr(self.user, 'full_name', ''),

            'current_level': getattr(self.user, 'current_level', 1),  # User 모델의 @property 사용 가정
            'level_xp': float(getattr(self.user, 'level_xp', 0.0)),

            'tier': tier_info_data,
            'user_tier_xp': float(getattr(self.user, 'user_tier_xp', 0.0)),

            'total_wins': getattr(self.user, 'total_wins', 0),
            'total_losses': getattr(self.user, 'total_losses', 0),

            'subscription_plan': getattr(self.user, 'subscription_plan', 'FREE'),
            'subscription_plan_display': subscription_plan_display_val,
            'current_subscription_end_date': current_subscription_end_date_val,

            'position_sharing_enabled': getattr(self.user, 'position_sharing_enabled', False),
            'is_2fa_enabled': getattr(self.user, 'is_2fa_enabled', False),

            'cash': float(getattr(self.user, 'cash', 0.0)),
            'real_cash': float(getattr(self.user, 'real_cash', 0.0)),
            'portfolio_value': float(getattr(self.user, 'portfolio_value', 0.0)),
            'asi_coin_balance': float(getattr(self.user, 'asi_coin_balance', Decimal('0.0'))),

            'wallet_address': getattr(self.user, 'wallet_address', None),
            'nickname_color': getattr(self.user, 'nickname_color', '#FFFFFF'),
        }
        data['user'] = user_data

        return data
