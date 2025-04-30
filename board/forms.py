# board/forms.py
from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    """일반 사용자용 게시글 폼"""
    class Meta:
        model = Post
        fields = ['title', 'content'] # 일반 사용자는 제목과 내용만 입력
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }

class AdminPostForm(forms.ModelForm):
    """관리자용 게시글 폼 (관리자 옵션 포함)"""
    class Meta:
        model = Post
        fields = ['title', 'content', 'is_notice', 'is_pinned', 'title_color'] # 관리자는 모든 필드 사용 가능
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }