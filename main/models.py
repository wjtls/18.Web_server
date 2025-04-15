from django.db import models

# Create your models here.
from django.db import models

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

class User(AbstractUser):
    # --- 기존 추가 필드들 ---
    cash = models.FloatField(default=1000000.0)
    symbol = models.CharField(max_length=10, null=True, blank=True)
    stock_count = models.IntegerField(default=0)
    portfolio_value = models.FloatField(default=1000000.0)
    level = models.IntegerField(default=1)
    user_tier = models.CharField(max_length=50, default="Bronze")
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