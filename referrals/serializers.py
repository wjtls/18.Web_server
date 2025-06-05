# referrals/serializers.py
from rest_framework import serializers
from django.conf import settings # WEB_BASE_URL 가져오기 위함

# User 모델을 가져오는 방법:
# 1. User 모델이 main 앱에 있다면 (가정):
from main.models import User
# 2. Django의 권장 방식 (settings.AUTH_USER_MODEL을 따름):
# from django.contrib.auth import get_user_model
# User = get_user_model()

def format_sensitive_text_serializer(text, visible_chars=4):
    """
    시리얼라이저 레벨에서 민감한 텍스트를 마스킹하는 헬퍼 함수.
    """
    if not text or not isinstance(text, str) or len(text) <= visible_chars:
        return text or 'N/A'
    return f"{text[:visible_chars]}{'*' * max(0, len(text) - visible_chars)}"

class ReferredUserSerializer(serializers.ModelSerializer):
    """
    추천 관련 목록 (내가 추천한 사용자, 나를 추천한 사용자)에 사용될 사용자 정보 시리얼라이저.
    API 응답에서 userId와 userCode는 여기서 마스킹 처리됨.
    """
    userId = serializers.SerializerMethodField()
    userCode = serializers.SerializerMethodField()
    registrationTime = serializers.DateTimeField(source='date_joined', format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = User
        fields = ['id', 'nickname', 'userId', 'userCode', 'registrationTime']

    def get_userId(self, obj):
        return format_sensitive_text_serializer(obj.username)

    def get_userCode(self, obj):
        # User 모델에 referral_code 필드가 있다고 가정
        return format_sensitive_text_serializer(obj.referral_code)


class MyReferralInfoSerializer(serializers.Serializer):
    """
    '나의 추천 정보' API 응답을 위한 시리얼라이저.
    뷰에서 구성한 딕셔너리를 받도록 설계됨.
    """
    my_referral_code = serializers.CharField(read_only=True)
    my_referral_link = serializers.SerializerMethodField()
    reward_policy = serializers.SerializerMethodField()
    upline_referrer = ReferredUserSerializer(allow_null=True, read_only=True)

    def get_my_referral_link(self, obj):
        """
        추천 코드를 사용하여 전체 추천 링크를 생성.
        obj는 뷰에서 전달된 딕셔너리이며, 'my_referral_code' 키를 포함해야 함.
        """
        referral_code = obj.get('my_referral_code')
        if referral_code:
            base_url = getattr(settings, 'WEB_BASE_URL', 'https://yourplatform.com') # settings.py에 WEB_BASE_URL 정의 권장
            return f"{base_url}/register?ref={referral_code}"
        return None

    def get_reward_policy(self, obj):
        """
        고정된 추천 보상 정책 정보를 반환.
        """
        return {
            "title": "추천인 보상 안내 (친구 구독 기준)",
            "description": "친구가 아래 유료 등급으로 신규 구독하고 결제를 완료하면, 결제액의 일정 비율이 현금으로 보상됩니다. 보상은 친구의 결제 완료 후 7일이 경과했을 때 책정되며, 매월 1일에 정산됩니다.",
            "tiers": [
                { "name": "BASIC", "reward_percentage": 5, "description": "친구가 Basic 등급 구독 시 친구 결제액의 5% 현금 보상" },
                { "name": "STANDARD", "reward_percentage": 10, "description": "친구가 Standard 등급 구독 시 친구 결제액의 10% 현금 보상" },
                { "name": "PREMIUM", "reward_percentage": 15, "description": "친구가 Premium 등급 구독 시 친구 결제액의 15% 현금 보상" }
            ],
            "notes": [
                "* 보상은 추천받은 친구가 실제 유료 구독 플랜으로 결제를 완료하고 7일이 경과했을 때 지급 대상이 됩니다.",
                "* 정산은 매월 1일에 이루어집니다.",
                "* 자세한 정책은 공지사항을 참고해주세요."
            ]
        }