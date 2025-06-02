from django.urls import path, include  # include 추가
from . import views  # 웹 뷰
from . import app_views  # API 뷰

app_name = 'board'

# API URL 패턴들을 별도로 그룹화 (선택적이지만 가독성 향상)
api_urlpatterns = [
    # Post APIs
    path('posts/', app_views.PostListCreateAPIView.as_view(), name='api_post_list_create'),
    path('posts/<int:pk>/', app_views.PostDetailAPIView.as_view(), name='api_post_detail'),

    # Comment APIs (게시글에 종속)
    path('posts/<int:post_pk>/comments/', app_views.CommentListCreateAPIView.as_view(), name='api_comment_list_create'),
    path('posts/<int:post_pk>/comments/<int:pk>/', app_views.CommentDetailAPIView.as_view(), name='api_comment_detail'),
    # 또는 /comments/<int:pk>/ 로 하고 view에서 post_pk 필터링

    # Like/Dislike API (Generic)
    path('content_types/<int:content_type_id>/objects/<int:object_id>/vote/<str:vote_type_str>/',
         app_views.vote_content_object, name='api_vote_object'),

    # User Search & Profile APIs
    path('users/', app_views.UserListAPIView.as_view(), name='api_user_list'),
    path('users/search/', app_views.UserSearchAPIView.as_view(), name='api_user_search'),
    path('users/<str:username>/profile/', app_views.UserProfileAPIView.as_view(), name='api_user_profile'),
    path('users/<str:username_to_follow>/follow_toggle/', app_views.FollowToggleAPIView.as_view(),name='api_follow_toggle'),
    path('users/<str:username>/following/', app_views.FollowingListAPIView.as_view(), name='api_user_following'),
    path('users/<str:username>/followers/', app_views.FollowersListAPIView.as_view(), name='api_user_followers'),
    path('posts/followed/', app_views.FollowedPostsAPIView.as_view(), name='api_posts_followed'),


    # Problem APIs
    path('problems/', app_views.ProblemListCreateAPIView.as_view(), name='api_problem_list_create'),
    path('problems/<int:pk>/', app_views.ProblemDetailAPIView.as_view(), name='api_problem_detail'),
    path('problems/attempts/', app_views.UserProblemAttemptCreateAPIView.as_view(), name='api_problem_attempt_create'),
    # 또는 path('problems/<int:problem_pk>/attempt/', ...)
]

urlpatterns = [
    # 기존 웹 URL
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.post_create, name='post_create'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),

    # API URLs - 네임스페이스 'api' 아래에 포함 (예: /board/api/posts/)
    path('api/', include(api_urlpatterns)),
]