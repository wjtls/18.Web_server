# main/forms.py

from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.conf import settings

User = get_user_model()
NICKNAME_BLACKLIST = getattr(settings, 'NICKNAME_BLACKLIST', ["운영자", "GM", "관리자", "admin","주인"])


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label=_("비밀번호"),
        widget=forms.PasswordInput(
            attrs={'class': 'form-control form-control-premium', 'placeholder': _('비밀번호 (8자 이상)')})  # 플레이스홀더 구체화
    )
    confirm_password = forms.CharField(
        label=_("비밀번호 확인"),
        widget=forms.PasswordInput(
            attrs={'class': 'form-control form-control-premium', 'placeholder': _('비밀번호를 다시 입력하세요')})
    )
    nickname = forms.CharField(
        label=_("닉네임"),
        max_length=50,
        widget=forms.TextInput(
            attrs={'class': 'form-control form-control-premium', 'placeholder': _('플랫폼에서 사용할 별명 (고유해야 함)')})
        # 플레이스홀더 구체화
    )
    full_name = forms.CharField(
        label=_("실명 (선택)"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-premium', 'placeholder': _('실명을 입력하세요')})
    )
    phone_number = forms.CharField(
        label=_("휴대폰 번호"),
        max_length=20,
        widget=forms.TextInput(
            attrs={'class': 'form-control form-control-premium', 'placeholder': _('예: 01012345678 (인증 필수)')}),
        # 플레이스홀더 구체화
        help_text=_("인증이 필요한 항목입니다.")
    )
    terms_accepted = forms.BooleanField(
        label=_("(필수) 이용약관 및 개인정보처리방침에 모두 동의합니다."),  # label 수정
        required=True
    )
    receive_platform_notifications = forms.BooleanField(
        label=_("(선택) 플랫폼 주요 알림 (서비스 공지, 업데이트 등) 수신"),  # label 수정
        required=False,
        initial=True
    )
    receive_marketing_notifications = forms.BooleanField(
        label=_("(선택) 마케팅 정보 (이벤트, 프로모션 등) 수신"),  # label 수정
        required=False,
        initial=False
    )

    class Meta:
        model = User
        fields = ['username', 'nickname', 'full_name', 'phone_number',  # password 필드들은 위에서 별도 정의
                  'terms_accepted', 'receive_platform_notifications', 'receive_marketing_notifications']
        widgets = {
            'username': forms.TextInput(
                attrs={'class': 'form-control form-control-premium', 'placeholder': _('사용하실 아이디를 입력하세요')}),
        }
        # email 필드가 User 모델에 있고 사용한다면 fields에 추가

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(_("비밀번호가 일치하지 않습니다."))
        # 항상 cleaned_data['confirm_password']를 반환하거나, 에러가 없으면 password를 반환할 수도 있습니다.
        return confirm_password  # 또는 password

    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        if nickname:
            for forbidden_word in NICKNAME_BLACKLIST:
                if forbidden_word.lower() in nickname.lower():
                    raise forms.ValidationError(
                        _("선택하신 닉네임에는 사용할 수 없는 단어가 포함되어 있습니다: %(word)s") % {'word': forbidden_word})

            # ModelForm은 unique=True 필드에 대한 중복 검사를 자동으로 수행 (self.instance가 설정되지 않은 경우 생성 시)
            # 만약 User 모델의 nickname 필드에 unique=True가 없다면 여기서 직접 검사:
            # if User.objects.filter(nickname__iexact=nickname).exists():
            #     raise forms.ValidationError(_("이미 사용 중인 닉네임입니다."))
        return nickname

    def save(self, commit=True):
        user = super().save(commit=False)  # username, nickname, full_name 등 Meta.fields에 명시된 것들 할당
        user.set_password(self.cleaned_data["password"])  # 비밀번호 해시 처리

        # User 모델에 정의된 필드에 맞게 cleaned_data에서 값을 가져와 할당
        # (Meta.fields에 없는 필드들이거나, 특별한 처리가 필요한 경우)
        user.receive_platform_notifications = self.cleaned_data.get('receive_platform_notifications', True)
        user.receive_marketing_notifications = self.cleaned_data.get('receive_marketing_notifications', False)

        # 기존 로직에서 설정하던 초기값들 (모델의 default로 설정하는 것이 더 좋을 수 있음)
        user.cash = 1000000.0
        user.portfolio_value = 1000000.0
        user.level_xp = 0.0
        user.user_tier = "Bronze"  # 또는 User 모델의 default 값인 "초보자"를 사용하거나, 여기서 명시적으로 "Bronze"
        user.real_cash = 0.0

        # phone_number와 phone_verified는 뷰에서 최종 인증 상태를 확인하고 설정할 예정

        if commit:
            user.save()
        return user


class NicknameChangeForm(forms.ModelForm):
    nickname = forms.CharField(
        label=_("새 닉네임"),
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'nicknameInput'}) # HTML의 id와 맞춤
    )

    class Meta:
        model = User
        fields = ['nickname']

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user_instance', None) # 뷰에서 현재 사용자 객체를 받음
        super().__init__(*args, **kwargs)

    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        if nickname:
            # 금칙어 확인
            for forbidden_word in NICKNAME_BLACKLIST:
                if forbidden_word.lower() in nickname.lower():
                    raise forms.ValidationError(
                        _("선택하신 닉네임에는 사용할 수 없는 단어가 포함되어 있습니다: %(word)s") % {'word': forbidden_word}
                    )
            # 현재 사용자의 닉네임과 다른 경우에만 중복 검사
            if self.user_instance and nickname.lower() == self.user_instance.nickname.lower():
                 # 현재 닉네임과 동일 (변경 안 함) - 오류 아님
                pass
            elif User.objects.filter(nickname__iexact=nickname).exists():
                raise forms.ValidationError(_("이미 사용 중인 닉네임입니다."))
        return nickname

class PositionSharingForm(forms.ModelForm):
    sharing_enabled = forms.BooleanField(
        required=False, # 체크 안 하면 False로 처리
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch', 'id': 'positionSharingSwitch'})
    )

    class Meta:
        model = User
        fields = ['position_sharing_enabled']