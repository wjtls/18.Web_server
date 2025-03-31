from django.db import models

# Create your models here.
from django.db import models

class AccessToken(models.Model): #DB저장 모델
    token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() >= self.expires_at