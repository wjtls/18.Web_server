
from django.db import models
from decimal import Decimal # Decimal 타입 import


class AccessToken(models.Model): #DB저장 모델
    token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() >= self.expires_at

# main/models.py (또는 해당 앱의 models.py)

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission # Group, Permission 모델도 import
from django.utils.translation import gettext_lazy as _ # 다국어 지원을 위한 verbose_name 등에서 사용될 수 있음
'''
class User(AbstractUser):
    # --- 기존 추가 필드들 ---
    cash = models.FloatField(default=1000000.0)
    symbol = models.CharField(max_length=10, null=True, blank=True)
    stock_count = models.IntegerField(default=0)
    portfolio_value = models.FloatField(default=1000000.0)
    level = models.IntegerField(default=1)
    user_tier = models.CharField(max_length=50, default="Bronze")
    real_cash = models.FloatField(default=0)
    # otp_secret = models.CharField(max_length=16, unique=True, null=True, blank=True) # 2FA 사용 시
    # is_2fa_enabled = models.BooleanField(default=False) # 2FA 사용 시

    # --- related_name 충돌 해결 ---
    # groups 필드를 재정의하며 고유한 related_name 추가
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        # ↓↓↓ 고유한 related_name 설정 ↓↓↓
        related_name="main_user_groups",
        related_query_name="user",
    )

    # user_permissions 필드를 재정의하며 고유한 related_name 추가
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        # ↓↓↓ 고유한 related_name 설정 ↓↓↓
        related_name="main_user_permissions",
        related_query_name="user",
    )

    def __str__(self):
        return self.username
    
'''

class User(AbstractUser):
    # --- 기존 추가 필드들 ---
    cash = models.FloatField(default=1000000.0)
    symbol = models.CharField(max_length=10, null=True, blank=True)
    stock_count = models.IntegerField(default=0)
    portfolio_value = models.FloatField(default=1000000.0)
    level = models.IntegerField(default=1)
    user_tier = models.CharField(max_length=50, default="Bronze")
    real_cash = models.FloatField(default=0)
    # otp_secret = models.CharField(max_length=16, unique=True, null=True, blank=True)
    # is_2fa_enabled = models.BooleanField(default=False)

    # --- ↓↓↓ ASI Coin 관련 필드 추가 ↓↓↓ ---

    asi_coin_balance = models.DecimalField(
        verbose_name=_("ASI 코인 잔액(오프체인)"),
        max_digits=38,     # 총 자릿수 (2000억 + 소수점 18자리 충분히 포함)
        decimal_places=18, # AsiCoin의 소수점 자릿수
        default=Decimal('0.0'), # 기본값은 0
        help_text=_("플랫폼 내부에서 사용하는 사용자의 오프체인 ASI 코인 잔액입니다.") # 관리자 화면 등 도움말
    )

    wallet_address = models.CharField(
        verbose_name=_("출금 지갑 주소"),
        max_length=42, # Ethereum/Polygon 주소 길이 ('0x' 포함 42자)
        blank=True,    # 사용자가 입력 안해도 됨 (필수 X)
        null=True,     # DB에 NULL 값 허용 (입력 안된 상태)
        unique=True,   # 하나의 지갑 주소는 한 명의 사용자만 등록 가능 (선택 사항)
        help_text=_("사용자가 ASI 코인을 외부로 출금할 때 사용할 개인 지갑 주소입니다 (예: 0x...).")
        # unique=True로 설정하면 여러 사용자가 같은 주소를 등록할 수 없음.
        # 고유할 필요가 없다면 unique=True 속성을 제거.
        # (null=True와 unique=True는 함께 사용 가능합니다. NULL 값은 고유성 제약 조건에 영향을 받지 않음.)
    )

    nickname = models.CharField(
        _("닉네임"),
        max_length=50,  # 닉네임 최대 길이 (원하는 대로 설정)
        unique=True,  # 닉네임 중복을 허용하지 않으려면 True, 허용하면 False (True 설정 시 동명이인 불가)
        blank=True,  # 회원가입 시 필수가 아니라면 True
        null=True,  # DB에 NULL값 허용 (blank=True 와 보통 같이 사용)
        help_text=_("플랫폼 내 활동 시 보여질 별명입니다.")
    )


    # --- ↓↓↓ 구독 플랜 필드 추가 ↓↓↓ ---
    # 구독 플랜 선택지 정의 (코드 가독성을 위해 상수로 정의)
    PLAN_FREE = 'FREE'
    PLAN_BASIC = 'BASIC'
    PLAN_STANDARD = 'STANDARD'
    PLAN_PREMIUM = 'PREMIUM'

    PLAN_CHOICES = [
        (PLAN_FREE, _('무료등급')),  # (DB에 저장될 실제 값, 화면에 보여질 이름)
        (PLAN_BASIC, _('베이직')),
        (PLAN_STANDARD, _('스탠다드')),
        (PLAN_PREMIUM, _('프리미엄')),
    ]

    # 구독 플랜 필드 정의
    subscription_plan = models.CharField(
        _("구독 플랜"),
        max_length=10,  # 선택지 값 중 가장 긴 문자열 길이 ('STANDARD')에 맞춤
        choices=PLAN_CHOICES,  # 위에서 정의한 선택지 목록 지정
        default=PLAN_FREE,  # 사용자가 처음 가입 시 기본값은 '무료등급'
        help_text=_("사용자의 현재 구독 플랜 등급입니다.")
    )



    # --- 기존 related_name 충돌 해결 부분 (제공해주신 내용 유지) ---
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="main_user_groups", # 제공해주신 related_name
        related_query_name="user",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="main_user_permissions", # 제공해주신 related_name
        related_query_name="user",
    )

    user_tier_xp = models.FloatField(  # 또는 DecimalField
        _("티어 경험치"),
        default=0.0,
        help_text=_("수익/손실에 따라 변동되는 티어 경험치입니다.")
    )

    position_sharing_enabled = models.BooleanField(
        _("포지션 공개 설정"),
        default=False,  # 기본값은 비공개
        help_text=_("프로필에서 포지션 공개 여부를 설정합니다. 수익 시 보상에 영향을 줄 수 있습니다.")
    )

    level_xp = models.FloatField(  # 또는 IntegerField (레벨 시스템 정책에 따라)
        _("레벨 경험치"),
        default=0.0,
        help_text=_("레벨업에 사용되는 경험치입니다. ASI 코인으로 구매 가능합니다.")
    )
    # 참고: 기존 'level' 필드는 이 'level_xp' 값에 따라 결정되도록 로직 변경 가능
    # 예: property나 별도 함수로 get_level() 등 구현

    nickname_color = models.CharField(
        _("닉네임 색상"),
        max_length=7,  # 예: '#RRGGBB' 형식
        default="#FFFFFF",  # 기본값 (예: 흰색)
        blank=True,
        help_text=_("채팅 등에서 사용될 닉네임 색상 코드입니다.")
    )

    #AI 트레이더 자동매매 구독시 소모 코인
    auto_trade_seconds_remaining = models.IntegerField(
        _("남은 자동매매 시간(초)"),
        default=0,
        help_text=_("ASI 코인으로 구매하여 충전된 자동매매 가능 시간(초 단위)입니다.")
    )

    def update_tier_xp(self, xp_change: float):
        """ User의 티어 경험치를 안전하게 업데이트 (DB 저장 포함) """
        try:
            # transaction.atomic을 사용하여 DB 업데이트의 원자성 보장
            with transaction.atomic():
                # select_for_update로 해당 레코드에 락(lock) 설정 (동시 업데이트 방지)
                user_to_update = User.objects.select_for_update().get(pk=self.pk)
                # F() 표현식을 사용하여 현재 DB 값 기준으로 안전하게 증감
                user_to_update.user_tier_xp = F('user_tier_xp') + xp_change
                user_to_update.save(update_fields=['user_tier_xp'])  # 변경된 필드만 저장
                user_to_update.refresh_from_db()  # DB에서 최신값 다시 읽기
                print(f"로그: 사용자 {self.username} 티어 경험치 {xp_change:+.1f} 적용. 현재 XP: {user_to_update.user_tier_xp:.1f}")

                # TODO: 여기서 경험치 변경에 따른 티어(user_tier) 변경 로직 추가 가능
                # new_tier = calculate_tier(user_to_update.user_tier_xp)
                # if user_to_update.user_tier != new_tier:
                #     user_to_update.user_tier = new_tier
                #     user_to_update.save(update_fields=['user_tier'])
                #     print(f"로그: 사용자 {self.username} 티어 변경 -> {new_tier}")

                return True
        except Exception as e:
            print(f"오류: 티어 경험치 업데이트 실패 (사용자: {self.username}): {e}")
            return False

    def __str__(self):
        return self.username


















# 구독 관련 모델

from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta

class SubscriptionBase(models.Model):
    """ 구독 정보 공통 베이스 모델 """
    subscriber = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="구독자")
    start_date = models.DateTimeField(auto_now_add=True, verbose_name="구독 시작일")
    expires_at = models.DateTimeField(verbose_name="구독 만료일")

    class Meta:
        abstract = True # 이 자체는 DB 테이블로 만들어지지 않음

    def is_active(self):
        return timezone.now() < self.expires_at
    is_active.boolean = True

class PositionViewSubscription(SubscriptionBase):
    """ 다른 사용자 포지션 보기 구독 정보 """
    target_trader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='position_subscribers', # 구독 대상 트레이더 입장에서의 관계 이름
        verbose_name="구독 대상 트레이더"
    )
    # ... (필요시 Meta 클래스 추가) ...

    def save(self, *args, **kwargs):
        # 생성 시 만료일 자동 설정 (7일)
        if not self.pk and not self.expires_at:
             self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    def __str__(self):
         return f"{self.subscriber.username} -> {self.target_trader.username} (만료: {self.expires_at.strftime('%Y-%m-%d %H:%M')})"













from django.utils import timezone
from datetime import timedelta
# ... (다른 import 및 User 모델 정의는 그대로) ...

# --- 기존 AITrader, AITraderSubscription 모델은 삭제 또는 주석 처리 ---
# class AITrader(models.Model): ...
# class AITraderSubscription(SubscriptionBase): ...

# --- ↓↓↓ 전략 페이지 구독 모델 새로 정의 ↓↓↓ ---
class StrategyPageSubscription(SubscriptionBase):
    """ 전략 페이지 접근 구독 정보 (SubscriptionBase 상속) """
    # subscriber, start_date, expires_at 필드는 SubscriptionBase 에서 가져옴
    # 특정 대상(ai_trader, target_trader)을 가리키는 필드는 필요 없음

    class Meta:
        verbose_name = "전략 페이지 구독"
        verbose_name_plural = "전략 페이지 구독 목록"
        ordering = ['-expires_at'] # 만료일 내림차순 정렬 (선택 사항)

    def save(self, *args, **kwargs):
        # 새로 생성될 때 만료일을 지금부터 7일 후로 설정
        if not self.pk and not self.expires_at:
             self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    def __str__(self):
        # 어떤 사용자가 구독 중인지 표시
        return f"{self.subscriber.username} - 전략 페이지 구독 (만료: {self.expires_at.strftime('%Y-%m-%d %H:%M')})"
# --- ↑↑↑ 전략 페이지 구독 모델 정의 완료 ↑↑↑ ---