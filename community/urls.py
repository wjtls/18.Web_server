# community/urls.py
from django.urls import path
from . import views

app_name = 'community' # 앱 네임스페이스 설정

urlpatterns = [
    path('', views.community_feed_view, name='community_feed'), # 커뮤니티 피드 페이지
    path('post/create/', views.create_post_view, name='create_post_url_name'), # 게시물 생성 (폼 제출 처리)
    path('post/<int:post_id>/like/', views.like_post_view, name='like_post'), # 좋아요 처리 API
    path('profile/<str:username>/', views.user_profile_view, name='user_profile_url_name'), # 사용자 프로필
    # path('post/<int:post_id>/', views.post_detail_view, name='post_detail_url_name'), # 게시물 상세 (댓글 모두 보기 등)
    # path('post/<int:post_id>/comment/add/', views.add_comment_view, name='add_comment_url_name'), # 댓글 추가
]