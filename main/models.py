
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

# models.py
from django.db import models, transaction
from django.db.models import F
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import math # 레벨 계산을 위해 math 모듈 임포트

# 티어 정보 정의 (임계값, 이름, 이미지 경로)
# 순서 중요: 높은 티어부터 낮은 티어 순으로 정의해야 get_tier_info에서 올바르게 작동
# 이미지는 예시 경로이며, 실제 static 파일 경로에 맞게 수정필요
# 랭커 정보는 함수에서 별도 처리
TIER_THRESHOLDS = [
    (40000, 'Champion', '🏆'),  # 챔피언: 트로피
    (20000, 'Grandmaster', '👑'),  # 그랜드마스터: 왕관
    (8000, 'Master', '🌟'),  # 마스터: 빛나는 별
    (4000, 'Diamond', '💎'),  # 다이아몬드: 보석
    (2000, 'Platinum', '💍'),  # 플래티넘: 별
    (1000, 'Gold', '🥇'),  # 골드: 금메달
    (500, 'Silver', '🥈'),  # 실버: 은메달
    (100, 'Bronze', '🥉'),  # 브론즈: 동메달
    (-float('inf'), '초보자', '🌱'), # 100점 미만 또는 초기 상태
]



class User(AbstractUser):
    # --- 기본 및 기존 필드 ---
    cash = models.FloatField(default=1000000.0)
    portfolio_value = models.FloatField(default=1000000.0)
    # level 필드는 이제 계산된 프로퍼티를 사용하므로, 직접 관리하지 않을 수 있음
    # level = models.IntegerField(default=1) # 필요하다면 유지 또는 @property로 대체
    user_tier = models.CharField(max_length=50, default="초보자") # 기본값 변경
    real_cash = models.FloatField(default=0)
    asi_coin_balance = models.DecimalField(
        verbose_name=_("ASI 코인 잔액(오프체인)"),
        max_digits=38, decimal_places=18, default=Decimal('0.0'),
        help_text=_("플랫폼 내부에서 사용하는 사용자의 오프체인 ASI 코인 잔액입니다.")
    )
    wallet_address = models.CharField(
        verbose_name=_("출금 지갑 주소"), max_length=42, blank=True, null=True, unique=True,
        help_text=_("사용자가 ASI 코인을 외부로 출금할 때 사용할 개인 지갑 주소입니다 (예: 0x...).")
    )
    wallet_verified = models.BooleanField(_("지갑 주소 인증 여부"), default=False)
    phone_number = models.CharField(_("휴대폰 번호"), max_length=20, blank=True, null=True)
    phone_verified = models.BooleanField(_("휴대폰 인증 여부"), default=False)
    nickname = models.CharField(
        _("닉네임"), max_length=50, unique=True, blank=True, null=True,
        help_text=_("플랫폼 내 활동 시 보여질 별명입니다.")
    )
    nickname_last_updated = models.DateTimeField(_("닉네임 마지막 변경일"), null=True, blank=True)
    subscription_plan = models.CharField(
        _("구독 플랜"), max_length=10, choices=[('FREE', _('무료등급')), ('BASIC', _('베이직')), ('STANDARD', _('스탠다드')), ('PREMIUM', _('프리미엄'))],
        default='FREE', help_text=_("사용자의 현재 구독 플랜 등급입니다.")
    )
    position_sharing_enabled = models.BooleanField(
        _("포지션 공개 설정"), default=False,
        help_text=_("프로필에서 포지션 공개 여부를 설정합니다. 수익 시 보상에 영향을 줄 수 있습니다.")
    )
    nickname_color = models.CharField(
        _("닉네임 색상"), max_length=7, default="#FFFFFF", blank=True,
        help_text=_("채팅 등에서 사용될 닉네임 색상 코드입니다.")
    )
    auto_trade_seconds_remaining = models.IntegerField(
        _("남은 자동매매 시간(초)"), default=0,
        help_text=_("ASI 코인으로 구매하여 충전된 자동매매 가능 시간(초 단위)입니다.")
    )

    # --- 레벨 관련 필드 및 로직 ---
    level_xp = models.FloatField(
        _("레벨 경험치"), default=0.0,
        help_text=_("레벨업에 사용되는 경험치입니다. ASI 코인으로 구매 가능합니다.")
    )

    # --- 전적 관련 필드 ---
    total_wins = models.IntegerField(_("총 승리"), default=0)
    total_losses = models.IntegerField(_("총 패배"), default=0)

    # --- 티어 관련 필드 ---
    user_tier_xp = models.FloatField(
        _("티어 경험치(포인트)"), default=0.0,
        help_text=_("수익/손실 및 수익률에 따라 변동되는 티어 포인트입니다.")
    )

    # --- 랭커 관련 필드 ---
    profit_rank = models.IntegerField(
        _("수익 랭킹"), null=True, blank=True, db_index=True, # 랭킹 계산 후 업데이트, 인덱스 추가
        help_text=_("전체 사용자 중 수익 기준 랭킹 (낮을수록 높음, 챔피언 티어 랭커 판별용)")
    )


    # --- ManyToMany 필드 (related_name 유지) ---
    groups = models.ManyToManyField(
        Group, verbose_name=_('groups'), blank=True,
        help_text=_('The groups this user belongs to...'),
        related_name="main_user_groups", related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission, verbose_name=_('user permissions'), blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="main_user_permissions", related_query_name="user",
    )

    # --- 메서드 및 프로퍼티 ---

    @property
    def current_level(self):
        """ 현재 레벨 경험치(level_xp)를 기준으로 레벨을 계산합니다. """
        xp = self.level_xp
        if xp < 1000:
            return 1
        # 레벨 L의 최소 요구 XP = 1000 * 2^(L-2)
        # xp >= 1000 * 2^(L-2)
        # xp / 1000 >= 2^(L-2)
        # log2(xp / 1000) >= L-2
        # L <= log2(xp / 1000) + 2
        # 단, xp가 정확히 경계값일 때 다음 레벨로 계산되지 않도록 처리 필요
        # 예를 들어 xp=1000일 때 L=2, xp=2000일 때 L=3
        level = math.floor(math.log2(xp / 1000)) + 2 if xp >= 1000 else 1
        # 경계값 확인: xp=1000 -> log2(1)+2=2, xp=2000 -> log2(2)+2=3, xp=4000->log2(4)+2=4
        # 정확히 경계값일 때 해당 레벨이 되므로 floor 사용이 적절
        return int(level) # 정수형으로 반환

    def add_level_xp(self, xp_amount: float):
        """ 레벨 경험치를 추가하고, 필요한 경우 레벨을 업데이트합니다. """
        if xp_amount == 0:
            return False # 변경 없으면 종료

        try:
            with transaction.atomic():
                user_locked = User.objects.select_for_update().get(pk=self.pk)
                current_xp_before = user_locked.level_xp
                current_level_before = user_locked.current_level # 변경 전 레벨 계산

                user_locked.level_xp = F('level_xp') + xp_amount
                user_locked.save(update_fields=['level_xp'])
                user_locked.refresh_from_db() # DB에서 최신 XP 읽기

                print(f"로그: 사용자 {self.username} 레벨 경험치 {xp_amount:+.1f} 적용. 현재 XP: {user_locked.level_xp:.1f}")

                # 레벨 변경 확인 및 업데이트
                new_level = user_locked.current_level
                if new_level > current_level_before:
                    # self.level 필드가 있다면 업데이트 (없으면 이 부분 불필요)
                    # user_locked.level = new_level
                    # user_locked.save(update_fields=['level'])
                    print(f"로그: 사용자 {self.username} 레벨 상승! {current_level_before} -> {new_level}")
                    # TODO: 레벨업 시 알림, 보상 등 추가 로직 실행 가능
                return True
        except Exception as e:
            print(f"오류: 레벨 경험치 업데이트 실패 (사용자: {self.username}): {e}")
            return False

    def record_trade_result(self, is_win: bool, profit_loss_percentage: float):
        """
        거래 결과를 기록하고 티어 경험치를 업데이트합니다.
        profit_loss_percentage: 수익률 (예: 0.1은 10% 수익, -0.05는 5% 손실)
        """
        if is_win and profit_loss_percentage <= 0:
             print(f"경고: 승리(is_win=True)로 기록되었으나 수익률({profit_loss_percentage})이 0 이하입니다.")
             # 필요시 에러 처리 또는 로직 조정
        if not is_win and profit_loss_percentage >= 0:
             print(f"경고: 패배(is_win=False)로 기록되었으나 손실률({profit_loss_percentage})이 0 이상입니다.")
             # 필요시 에러 처리 또는 로직 조정

        try:
            with transaction.atomic():
                user_locked = User.objects.select_for_update().get(pk=self.pk)
                current_tier_before = user_locked.get_tier_info()['name']

                # 1. 전적 업데이트
                if is_win:
                    user_locked.total_wins = F('total_wins') + 1
                    update_fields_trade = ['total_wins']
                    print(f"로그: 사용자 {self.username} 1승 추가. 총 {user_locked.total_wins + 1}승")
                else:
                    user_locked.total_losses = F('total_losses') + 1
                    update_fields_trade = ['total_losses']
                    print(f"로그: 사용자 {self.username} 1패 추가. 총 {user_locked.total_losses + 1}패")
                user_locked.save(update_fields=update_fields_trade)
                user_locked.refresh_from_db() # 전적 업데이트 반영

                # 2. 티어 포인트 계산 및 업데이트
                # 승리: +10 * 수익률, 패배: -10 * |손실률|
                points_change = 10 * abs(profit_loss_percentage)
                if not is_win:
                    points_change *= -1

                user_locked.user_tier_xp = F('user_tier_xp') + points_change
                user_locked.save(update_fields=['user_tier_xp'])
                user_locked.refresh_from_db() # 티어 포인트 업데이트 반영

                print(f"로그: 사용자 {self.username} 티어 포인트 {points_change:+.2f} 적용 ({'승' if is_win else '패'}, 수익률: {profit_loss_percentage:.2%}). 현재 포인트: {user_locked.user_tier_xp:.2f}")

                # 3. 티어 이름 업데이트 확인
                new_tier_info = user_locked.get_tier_info()
                new_tier_name = new_tier_info['name'] # 'Ranker 15' 같은 형태 포함

                # user_tier 필드에 저장될 기본 티어 이름 (랭크 숫자 제외)
                base_tier_name = new_tier_name.split(' ')[0] if 'Ranker' in new_tier_name else new_tier_name

                if user_locked.user_tier != base_tier_name:
                    user_locked.user_tier = base_tier_name
                    user_locked.save(update_fields=['user_tier'])
                    print(f"로그: 사용자 {self.username} 티어 변경! {current_tier_before} -> {new_tier_name}")
                    # TODO: 티어 변경 시 알림 등 추가 로직

                return True

        except Exception as e:
            print(f"오류: 거래 결과 기록 실패 (사용자: {self.username}): {e}")
            return False

    def get_tier_info(self):
        """
        현재 티어 경험치(user_tier_xp)와 **미리 계산된 포트폴리오 가치 랭킹(profit_rank)**을 기준으로
        티어 정보(이름, 이모지, 랭크 숫자)를 반환합니다.

        **중요:** self.profit_rank 필드는 **반드시 외부 프로세스(예: 스케줄된 작업)에 의해**
              주기적으로 모든 사용자의 portfolio_value를 기준으로 계산되어 **업데이트되어야**
              정확한 랭커 판별이 가능합니다. 이 메서드는 저장된 profit_rank 값을 읽기만 합니다.
        """
        xp = self.user_tier_xp
        # profit_rank 필드는 외부에서 portfolio_value 기준으로 계산되어 업데이트되었다고 가정
        rank = self.profit_rank

        current_tier = None
        # TIER_THRESHOLDS 순회 (이모지를 'image' 키로 사용한 사용자의 코드 기준)
        for threshold, name, image_or_emoji in TIER_THRESHOLDS:
            if xp >= threshold:
                # 'image' 키를 사용하되, 값은 이모지 문자열
                current_tier = {'name': name, 'image': image_or_emoji, 'rank_number': None}
                break

        # 티어가 결정되지 않은 경우 초보자로 처리 (마지막 항목 사용)
        if current_tier is None:
            threshold, name, image_or_emoji = TIER_THRESHOLDS[-1]
            current_tier = {'name': name, 'image': image_or_emoji, 'rank_number': None}

        # 챔피언 티어 & 랭커 조건 확인
        # 1. 기본 티어가 챔피언인가? (XP 조건 만족)
        # 2. profit_rank 값이 유효한가? (None이 아니고 1~50 사이)
        if current_tier['name'] == 'Champion' and rank is not None and 1 <= rank <= 50:
            # 조건 만족 시 랭커 정보로 덮어쓰기
            current_tier['name'] = f"Ranker ({rank} 위)" # 사용자가 제공한 이름 형식
            current_tier['rank_number'] = rank # 프론트엔드에서 숫자 표시용

        return current_tier


    # --- 기존 메서드들 ---
    def update_tier_xp(self, xp_change: float):
        """ User의 티어 경험치(포인트)를 직접 업데이트 (거래 결과 외, 예: 이벤트 보상) """
        try:
            with transaction.atomic():
                user_locked = User.objects.select_for_update().get(pk=self.pk)
                current_tier_before = user_locked.get_tier_info()['name']

                user_locked.user_tier_xp = F('user_tier_xp') + xp_change
                user_locked.save(update_fields=['user_tier_xp'])
                user_locked.refresh_from_db()
                print(f"로그: 사용자 {self.username} 티어 포인트 {xp_change:+.2f} 직접 적용. 현재 포인트: {user_locked.user_tier_xp:.2f}")

                # 티어 이름 업데이트 확인
                new_tier_info = user_locked.get_tier_info()
                new_tier_name = new_tier_info['name']
                base_tier_name = new_tier_name.split(' ')[0] if 'Ranker' in new_tier_name else new_tier_name

                if user_locked.user_tier != base_tier_name:
                    user_locked.user_tier = base_tier_name
                    user_locked.save(update_fields=['user_tier'])
                    print(f"로그: 사용자 {self.username} 티어 변경! {current_tier_before} -> {new_tier_name}")

                return True
        except Exception as e:
            print(f"오류: 티어 포인트 직접 업데이트 실패 (사용자: {self.username}): {e}")
            return False

    def can_change_nickname(self):
        if not self.nickname_last_updated:
            return True
        # nickname_last_updated가 timezone-aware datetime인지 확인 필요
        # Django 설정(USE_TZ=True)에 따라 다름
        if timezone.is_naive(self.nickname_last_updated):
             # Naive datetime이면 현재 시간도 naive로 비교
             now = timezone.make_naive(timezone.now(), timezone.get_current_timezone())
             return now >= self.nickname_last_updated + timedelta(minutes=5)
        else:
             # Aware datetime이면 그대로 비교
             return timezone.now() >= self.nickname_last_updated + timedelta(minutes=5)


    def __str__(self):
        return self.username






from django.db import models
from django.conf import settings # settings.AUTH_USER_MODEL 사용 위해


class Holding(models.Model):
    """사용자의 개별 보유 종목 정보를 저장하는 모델"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, # User 모델과 연결 (settings 사용하는 것이 좋음)
        on_delete=models.CASCADE, # 사용자가 삭제되면 보유 종목도 삭제
        related_name='holdings'   # User 객체에서 .holdings 로 접근 가능하게 함
    )
    symbol = models.CharField(max_length=20, db_index=True) # 종목 심볼 (예: TQQQ, AAPL), 인덱스 추가 권장
    quantity = models.IntegerField(default=0)               # 보유 수량
    avg_price = models.FloatField(default=0.0)              # 평균 매수 단가

    class Meta:
        unique_together = ('user', 'symbol') # 한 사용자는 같은 종목을 하나만 보유 (중복 방지)
        verbose_name = "보유 종목"
        verbose_name_plural = "보유 종목 목록"

    def __str__(self):
        return f"{self.user.username} - {self.symbol}: {self.quantity} @ {self.avg_price}"

    @property
    def current_value(self):
        # 실시간 현재가를 가져오는 로직 필요 (별도 함수 또는 서비스 연동)
        # 여기서는 임시로 avg_price 사용
        # current_price = get_current_price(self.symbol) # 이런 함수가 있다고 가정
        # return self.quantity * current_price
        return self.quantity * self.avg_price # 임시 계산

    @property
    def purchase_value(self):
        """총 매수 금액"""
        return self.quantity * self.avg_price

    @property
    def profit_loss(self):
        """평가 손익"""
        return self.current_value - self.purchase_value

    @property
    def return_percentage(self):
        """수익률"""
        if self.purchase_value == 0:
            return 0.0
        return (self.profit_loss / self.purchase_value) * 100



# 보유종목

class Trade(models.Model):
    """
    사용자의 주식/코인 거래(매수/매도 체결) 기록을 저장하는 모델
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, # 이 거래를 한 사용자
        on_delete=models.CASCADE, # 사용자가 삭제되면 관련 거래 기록도 삭제
        related_name='trades'     # User 객체에서 .trades 로 접근 가능하게 함
    )
    symbol = models.CharField(max_length=20, db_index=True) # 거래된 종목 심볼 (예: TQQQ, KRW-BTC)
    action = models.CharField(
        max_length=4, # 'buy' 또는 'sell'
        choices=[('buy', '매수'), ('sell', '매도')], # 선택지를 명확히 정의
        db_index=True # 조회 성능을 위해 인덱스 추가
    )
    quantity = models.FloatField()  # 거래 수량 (소수점이 가능하도록 FloatField 사용)
    price = models.FloatField()       # 체결 단가 (소수점이 가능하도록 FloatField 사용)
    # 매도 거래 시의 손익을 저장 (USD 또는 KRW 등 기준은 통일 필요). 매수 시에는 None
    profit = models.FloatField(null=True, blank=True)
    # 거래 체결 시간 (레코드가 생성될 때 자동으로 현재 시간 저장 및 인덱스 추가)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "거래 기록"
        verbose_name_plural = "거래 기록 목록"
        ordering = ['-timestamp'] # 기본 정렬: 최신 거래 내역이 가장 먼저 오도록 (-는 내림차순)

    def __str__(self):
        # __str__ 메서드에서 action choices 값을 사람이 읽기 좋게 표시
        action_display = dict(self._meta.get_field('action').choices).get(self.action, self.action)
        # 시간 형식은 필요에 따라 조정
        timestamp_display = self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else '시간 정보 없음'
        return f"{self.user.username} - {self.symbol} {action_display} {self.quantity}주 @ {self.price:.2f} ({timestamp_display})"




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




from django.db.models import Window, F
from django.db.models.functions import Rank
from .models import User # User 모델 임포트

def update_portfolio_rankings():
    """ 모든 사용자의 portfolio_value를 기준으로 순위를 매겨 profit_rank 필드를 업데이트. """
    print("포트폴리오 랭킹 업데이트 시작...")

    # Window 함수를 사용하여 DB 레벨에서 랭킹 계산 (효율적)
    # portfolio_value가 높은 순서대로 랭크 부여 (1위, 2위, ...)
    users_to_update = User.objects.annotate(
        current_rank=Window(
            expression=Rank(),
            order_by=F('portfolio_value').desc() # portfolio_value 내림차순
        )
    )

    # 계산된 랭킹으로 각 사용자의 profit_rank 필드 업데이트
    # bulk_update 사용이 더 효율적일 수 있음
    updated_count = 0
    for user in users_to_update:
        # 랭킹이 변경되었거나 기존 랭킹이 없을 때만 업데이트 (선택적 최적화)
        if user.profit_rank != user.current_rank:
            user.profit_rank = user.current_rank
            user.save(update_fields=['profit_rank'])
            updated_count += 1

    print(f"포트폴리오 랭킹 업데이트 완료. {updated_count}명 업데이트됨.")









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