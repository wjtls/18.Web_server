# community/forms.py
from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image', 'caption'] # 사용자가 입력할 필드
        widgets = {
            'caption': forms.Textarea(attrs={'rows': 3, 'placeholder': '문구를 입력하세요...'}),
            'image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }
        labels = { # 폼 필드의 한글 레이블 (선택적)
            'image': '이미지',
            'caption': '내용',
        }