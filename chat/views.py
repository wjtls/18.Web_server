# chat/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required # 로그인한 사용자만 접근 가능
def chat_view(request):
    # DB에서 메시지를 미리 불러와서 넘겨주는 것도 가능하지만,
    # 여기서는 Consumer에서 웹소켓 연결 시 보내주므로 굳이 안 해도 됨.
    return render(request, 'chat/chat_room.html')