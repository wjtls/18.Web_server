from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from chat.models import ChatMessage  # 우리가 만든 ChatMessage 모델


class Command(BaseCommand):
    help = 'Deletes chat messages older than 10 days.'  # 명령어 도움말

    def handle(self, *args, **options):
        # 10일 전 날짜 계산
        ten_days_ago = timezone.now() - timedelta(days=10)

        # 10일보다 오래된 메시지들 선택
        old_messages = ChatMessage.objects.filter(timestamp__lt=ten_days_ago)

        # 삭제된 메시지 수 카운트
        count, _ = old_messages.delete()

        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} old chat messages.'))
        # 서버 로그에도 기록되도록 print 사용 가능
        print(f'[{timezone.now()}] Deleted {count} chat messages older than 10 days.')