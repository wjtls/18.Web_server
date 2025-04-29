# python manage.py createsuperuser 생성
# http://127.0.0.1:8000/admin/ 관리자페이지


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

# 관리자 페이지에 등록할 모델들을 models.py 에서 가져옵니다.
from .models import User, PositionViewSubscription, StrategyPageSubscription
# AccessToken 모델도 관리하려면 import 하세요:
# from .models import AccessToken
# AITrader 모델도 만들었다면 import 하세요:
# from .models import AITrader

# 1. User 모델 관리자 화면 설정 (커스터마이징)
# --------------------------------------------------
@admin.register(User) # @admin.register 데코레이터 사용 방식
class UserAdmin(BaseUserAdmin):
    """ User 모델을 위한 커스텀 관리자 화면 설정 """

    # --- 관리자 목록 화면 설정 ---
    # ★★★ list_display는 'level', 'user_tier'를 그대로 유지 ★★★
    list_display = (
        'username',
        'email',
        'nickname',
        'asi_coin_balance_display',
        'subscription_plan',
        'level',          # models.User의 필드가 아니지만, 아래 정의된 level 메서드가 호출됨
        'user_tier',      # models.User의 필드가 아니지만, 아래 정의된 user_tier 메서드가 호출됨
        'is_staff',
        'is_active',
        'date_joined',
    )
    list_filter = BaseUserAdmin.list_filter + ('subscription_plan', 'user_tier', 'position_sharing_enabled', 'is_active', 'is_staff')
    search_fields = ('username', 'nickname', 'email', 'wallet_address', 'phone_number')
    ordering = ('-date_joined',)

    # --- 사용자 상세 정보/수정 화면 설정 (섹션별 그룹화) ---
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Profile Settings'), {'fields': ('nickname', 'nickname_color', 'nickname_last_updated', 'phone_number', 'phone_verified')}),
        (_('ASI Coin & Wallet'), {'fields': ('asi_coin_balance', 'wallet_address', 'wallet_verified')}),
        # ★★★ 'Platform Activity' 섹션에서 'level' 필드 제거 (필수!) ★★★
        (_('Platform Activity'), {'fields': (
            'level_xp',  # 실제 레벨 경험치 필드
            'user_tier', # ★★★ 여기서는 models.User의 user_tier 필드를 참조함 ★★★
            'user_tier_xp',
            'total_wins',
            'total_losses',
            'profit_rank',
            'position_sharing_enabled',
            'subscription_plan'
        )}),
        (_('Trading Info'), {'fields': ('cash', 'real_cash', 'portfolio_value', 'symbol', 'stock_count')}),
        (_('Auto Trading'), {'fields': ('auto_trade_seconds_remaining',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('Profile'), {'fields': ('nickname',)}),
    )

    # ★★★ profit_rank는 읽기 전용으로 추가하는 것이 좋음 ★★★
    readonly_fields = ('last_login', 'date_joined', 'nickname_last_updated', 'profit_rank')

    # list_display의 'asi_coin_balance_display'를 위한 메서드 (기존 유지)
    @admin.display(description='ASI 코인 잔액')
    def asi_coin_balance_display(self, obj):
        return "{:,.4f}".format(obj.asi_coin_balance)

    # ★★★ list_display의 'level' 항목을 처리하기 위한 메서드 ★★★
    @admin.display(description='Level', ordering='level_xp') # level_xp 기준으로 정렬
    def level(self, obj):
        """ User 모델의 current_level 프로퍼티 값을 반환 """
        # obj는 User 인스턴스
        return obj.current_level

    # ★★★ list_display의 'user_tier' 항목을 처리하기 위한 메서드 ★★★
    @admin.display(description='Tier', ordering='user_tier_xp') # user_tier_xp 기준으로 정렬
    def user_tier(self, obj):
        """ User 모델의 get_tier_info() 결과를 사용하여 이모지와 이름을 반환 """
        # obj는 User 인스턴스
        tier_info = obj.get_tier_info()
        # get_tier_info에서 반환하는 딕셔너리의 이모지 키가 'image'인지 확인 (사용자 코드 기준)
        emoji = tier_info.get('image', '')
        name = tier_info.get('name', 'N/A')
        # rank_number = tier_info.get('rank_number') # 필요시 랭커 번호도 포함 가능

        return f"{emoji} {name}"


# 2. 구독 정보 관리자 화면 설정 (공통 베이스)
# --------------------------------------------------
class SubscriptionAdmin(admin.ModelAdmin):
    """ 구독 모델들을 위한 공통 관리자 화면 설정 (상속용) """
    list_display = ('subscriber_link', 'start_date', 'expires_at', 'is_active') # 목록 표시 필드
    list_filter = ('expires_at',) # 필터 (만료일 기준)
    search_fields = ('subscriber__username', 'subscriber__nickname') # 구독자 아이디/닉네임 검색
    # 생성/수정 화면에서 읽기 전용 필드
    readonly_fields = ('subscriber', 'start_date', 'expires_at', 'is_active')
    ordering = ('-expires_at',) # 만료일 내림차순 정렬

    # 구독자 필드를 클릭 가능한 링크로 만들기
    @admin.display(description='구독자', ordering='subscriber__username')
    def subscriber_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        link = reverse("admin:main_user_change", args=[obj.subscriber.pk]) # 'main'은 앱 이름, 'user'는 모델 소문자 이름
        return format_html('<a href="{}">{}</a>', link, obj.subscriber.username)

    # is_active 필드를 boolean 아이콘으로 표시
    @admin.display(boolean=True, description='활성 여부')
    def is_active(self, obj):
        return obj.is_active()

# 3. PositionViewSubscription 모델 관리자 화면 등록
# --------------------------------------------------
@admin.register(PositionViewSubscription)
class PositionViewSubscriptionAdmin(SubscriptionAdmin): # 공통 베이스 상속
    """ PositionViewSubscription 모델 관리자 설정 """
    list_display = ('subscriber_link', 'target_trader_link', 'start_date', 'expires_at', 'is_active') # target_trader 추가
    search_fields = SubscriptionAdmin.search_fields + ('target_trader__username', 'target_trader__nickname') # 대상 트레이더 검색 추가

    # 대상 트레이더 필드를 클릭 가능한 링크로 만들기
    @admin.display(description='구독 대상', ordering='target_trader__username')
    def target_trader_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        link = reverse("admin:main_user_change", args=[obj.target_trader.pk]) # 'main_user'는 앱이름_모델소문자
        return format_html('<a href="{}">{}</a>', link, obj.target_trader.username)

# 4. StrategyPageSubscription 모델 관리자 화면 등록
# --------------------------------------------------
@admin.register(StrategyPageSubscription)
class StrategyPageSubscriptionAdmin(SubscriptionAdmin): # 공통 베이스 상속
    """ StrategyPageSubscription 모델 관리자 설정 """
    # 특별히 추가할 설정 없으면 pass 사용 가능. 공통 설정 그대로 사용.
    pass


# 5. AccessToken 모델 관리자 화면 등록 (models.py에 있다면)
# --------------------------------------------------
# @admin.register(AccessToken)
# class AccessTokenAdmin(admin.ModelAdmin):
#     list_display = ('token', 'expires_at', 'is_expired')
#     list_filter = ('expires_at',)
#     readonly_fields = ('is_expired',)


# 6. AITrader 모델 관리자 화면 등록 (models.py에 있다면)
# --------------------------------------------------
# @admin.register(AITrader)
# class AITraderAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description')
#     search_fields = ('name',)