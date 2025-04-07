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


# --- 회원가입 뷰 함수 ---
def register_view(request): #회원가입시 처리
    if request.method == 'POST':
        # 폼에서 데이터 가져오기
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        terms_accepted = request.POST.get('terms_accepted') # 체크박스 값 가져오기

        # --- 유효성 검사 ---
        # 1. 필수 약관 동의 확인
        if not terms_accepted:
            messages.error(request, '이용약관 및 개인정보처리방침에 동의해야 합니다.')
            # 동의 안했을 경우, 보통 원래 있던 페이지로 돌아가게 합니다.
            # 여기서는 홈페이지('/')로 리다이렉트하는 예시를 보여드립니다.
            # 실제로는 모달이 있던 페이지로 돌아가도록 URL을 지정하는 것이 좋습니다.
            # referer = request.META.get('HTTP_REFERER', '/')
            # return redirect(referer)
            return redirect('/') # 예시: 홈페이지로 리다이렉트

        # 2. 비밀번호 일치 확인
        if password != confirm_password:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
            return redirect('/') # 예시: 홈페이지로 리다이렉트

        # 3. 사용자 이름 중복 확인
        if User.objects.filter(username=username).exists():
            messages.error(request, '이미 사용 중인 사용자 이름입니다.')
            return redirect('/') # 예시: 홈페이지로 리다이렉트

        # 4. (선택 사항) 비밀번호 복잡성 검사 등 추가 가능

        # --- 사용자 생성 ---
        try:
            user = User.objects.create_user(username=username, password=password)
            # user.email = '...' # 이메일 등 추가 정보가 있다면 여기서 설정
            # user.save() # create_user 사용 시 자동 저장되므로 보통 불필요

            # --- 회원가입 후 자동 로그인 (선택 사항) ---
            # login(request, user) # 주석 해제 시 자동 로그인 활성화

            messages.success(request, '회원가입이 완료되었습니다. 로그인해주세요.') # 또는 자동 로그인 시 '환영합니다!'
            return redirect('login') # 로그인 페이지로 리다이렉트 (또는 홈페이지 등)

        except Exception as e:
            messages.error(request, f'회원가입 중 오류가 발생했습니다: {e}')
            return redirect('/') # 예시: 홈페이지로 리다이렉트

    else:
        # GET 요청 처리 (보통 회원가입 페이지를 직접 보여줄 때 사용)
        # 모달 방식에서는 POST만 처리하는 경우가 많지만,
        # 만약 register/ URL로 직접 접근했을 때의 처리를 원한다면 여기에 로직 추가
        # 예: return render(request, 'main/register_page.html')
        # 여기서는 GET 요청 시 홈페이지로 돌려보내는 것으로 처리합니다.
        return redirect('/')
