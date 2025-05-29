# board/urls.py
from django.urls import path
from . import views
from . import app_views # app_views.py 에서 API 뷰들을 가져옵니다.

app_name = 'board' # 앱 네임스페이스 설정

urlpatterns = [
    path('', views.post_list, name='post_list'), # 게시글 목록
    path('post/<int:pk>/', views.post_detail, name='post_detail'), # 게시글 상세
    path('post/new/', views.post_create, name='post_create'), # 새 글 작성
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'), # 글 수정
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'), # 글 삭제

    # 앱과 웹게시글 연동
    path('posts/', app_views.PostListCreateAPIView.as_view(), name='api_post_list_create'),
    path('posts/<int:pk>/', app_views.PostDetailAPIView.as_view(), name='api_post_detail'),
]