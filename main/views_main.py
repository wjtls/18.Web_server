from django.shortcuts import render
from django.http import HttpResponse
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate # 자동 로그인을 위해 login 추가
from django.contrib import messages # 사용자에게 피드백 메시지를 보여주기 위함


def index(request):
    return render(request,"main/index_homepage.html")

def index2_simulator(request):
    return render(request,"main/index2_simulator.html")

def index3_strategy(request):
    return render(request,"main/index3_strategy.html")

def index4_user_market(request):
    return render(request,"main/index4_user_market.html")

def chat_return(request): #채팅을 리턴
    data = request.POST.get("message")
    print(data,'채팅창에 입력된 문자')
    return HttpResponse(data)


from django.shortcuts import render, redirect
from django.contrib import messages
# from django.contrib.auth.hashers import make_password # create_user 사용 시 필요 없음
from .models import User # 사용자 모델 import

def register_view(request):
    """
    회원가입 요청을 처리하는 뷰 함수 (POST 요청만 처리)
    """
    if request.method == 'POST':
        # 폼에서 데이터 가져오기
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        terms_accepted = request.POST.get('terms_accepted')

        # 1. 필수 항목 검사
        if not all([username, password, confirm_password]):
            messages.error(request, '모든 필수 항목을 입력해주세요.')
            return redirect('_register_modal.html')

        # 2. 비밀번호 일치 확인
        if password != confirm_password:
            messages.warning(request, '비밀번호가 일치하지 않습니다.')
            return redirect('_register_modal.html')

        # 3. 약관 동의 확인
        if terms_accepted != 'true':
            messages.warning(request, '이용약관 및 개인정보처리방침에 동의해야 합니다.')
            return redirect('_register_modal.html')

        # 4. 기존 사용자 확인
        if User.objects.filter(username=username).exists():
            messages.warning(request, '이미 사용 중인 사용자 이름입니다.')
            return redirect('_register_modal.html')

        # 5. 새 사용자 생성 (create_user 사용)
        # User.objects.create_user() 사용: 비밀번호 해싱 및 저장을 자동으로 처리
        new_user = User.objects.create_user(
            username=username,
            password=password, # 원본 비밀번호 전달
            # --- 추가 필드 값 설정 ---
            cash = 1000000,
            portfolio_value = 1000000,
            level = 1,
            user_tier = "Bronze",
            real_cash = 0,  # 진짜 돈
            # otp_secret 설정 등 필요시 추가
        )
        # create_user는 객체를 생성하고 바로 save()까지 호출
        # 따라서 new_user.save() 를 별도로 호출할 필요가 없음

        messages.success(request, f'{username}님, 회원가IP 성공! 로그인해주세요.')
        return redirect('index')


    # POST 요청이 아닐 경우 (예: 직접 /register/ URL로 접근 시도)
    # 보통 회원가입 폼을 보여주는 GET 요청 처리가 필요하지만,
    # 모달 형태라면 그냥 메인 페이지로 보내는 것이 자연스러울 수 있습니다.
    return redirect('index')


from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    # 이 뷰 함수는 로그인된 사용자만 접근할 수 있도록
    return redirect('index')