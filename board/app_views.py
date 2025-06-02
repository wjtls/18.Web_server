from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q  # Q 객체 임포트

from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser  # 파일 업로드용
from django_filters.rest_framework import DjangoFilterBackend

from .models import Post, Comment, LikeDislike, UserFollow, Problem, ProblemChoice, UserProblemAttempt
from .serializers import (
    PostSerializer, CommentSerializer, LikeDislikeSerializer, UserFollowSerializer,
    ProblemSerializer, UserProblemAttemptSerializer, UserProfileSerializer,
    AuthorDisplaySerializer  # 사용자 검색용
)
from .permissions import IsOwnerOrReadOnly, IsStaffOrReadOnly  # 커스텀 권한




from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend

# UserFollow 모델을 가져오기 위해 models에서 모든 것을 가져오거나 특정 모델만 지정합니다.
from .models import Post, Comment, LikeDislike, UserFollow, Problem, ProblemChoice, UserProblemAttempt
from .serializers import (
    PostSerializer, CommentSerializer, LikeDislikeSerializer, UserFollowSerializer,
    ProblemSerializer, UserProblemAttemptSerializer, UserProfileSerializer,
    AuthorDisplaySerializer
)
from .permissions import IsOwnerOrReadOnly, IsStaffOrReadOnly
from django.db.models import Count, Q # Q 객체는 이미 임포트되어 있을 수 있습니다. Count 추가
from .models import Post, Comment, LikeDislike, UserFollow, Problem, ProblemChoice, UserProblemAttempt # LikeDislike 임포트 확인

User = get_user_model()


# --- 기존 Post API Views (수정) ---
class PostListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['is_notice', 'author__username', 'is_anonymous']
    search_fields = ['title', 'content', 'author__username', 'author__nickname']
    # 어노테이트된 필드명으로 변경
    ordering_fields = ['created_at', 'is_pinned', 'annotated_likes_count', 'annotated_comment_count']

    def get_queryset(self):
        queryset = Post.objects.select_related('author').prefetch_related('files', 'comments', 'likes_dislikes')

        queryset = queryset.annotate(
            # 어노테이션 필드 이름을 모델 프로퍼티와 다르게 지정
            annotated_likes_count=Count('likes_dislikes', filter=Q(likes_dislikes__vote_type=LikeDislike.LIKE),
                                        distinct=True),
            annotated_comment_count=Count('comments', distinct=True)  # 댓글 수도 중복 방지 위해 distinct=True 고려
        )
        return queryset.all()

    def perform_create(self, serializer):
        serializer.save()



class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.select_related('author').prefetch_related('files', 'comments', 'likes_dislikes').all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]  # 수정/삭제는 작성자 또는 관리자만
    parser_classes = [MultiPartParser, FormParser]  # 파일 수정도 고려 (현재 Serializer는 제한적)

    # perform_update, perform_destroy는 기본 동작 사용 또는 필요시 오버라이드


class UserListAPIView(generics.ListAPIView):
    """
    사용자 목록을 반환합니다. 추천 사용자 등에 활용될 수 있습니다.
    정렬 및 필터링은 필요에 따라 추가할 수 있습니다.
    """
    queryset = User.objects.filter(is_active=True).order_by('-date_joined')  #  최근 가입자 순
    serializer_class = AuthorDisplaySerializer  # 프로필 이미지 등을 포함하는 Serializer
    permission_classes = [permissions.AllowAny]  # 누구나 볼 수 있도록 설정 (또는 IsAuthenticated)
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]  # 기본 필터 추가


# --- Comment API Views ---
class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_pk = self.kwargs.get('post_pk')
        post = get_object_or_404(Post, pk=post_pk)
        # 최상위 댓글만 가져오기 (parent_comment=None)
        return Comment.objects.filter(post=post, parent_comment=None).select_related('author').prefetch_related(
            'replies', 'likes_dislikes').all()

    def perform_create(self, serializer):
        post_pk = self.kwargs.get('post_pk')
        post = get_object_or_404(Post, pk=post_pk)
        # serializer.save(author=self.request.user, post=post) # Serializer의 create에서 author 처리
        serializer.save(post=post)


class CommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        post_pk = self.kwargs.get('post_pk')  # URL에서 post_pk를 받도록 설정 필요
        return Comment.objects.filter(post_id=post_pk).select_related('author').prefetch_related('replies',
                                                                                                 'likes_dislikes').all()

    # lookup_url_kwarg = 'comment_pk' # URL에서 댓글 pk를 comment_pk로 받는 경우


# --- Like/Dislike API View ---
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def vote_content_object(request, content_type_id, object_id, vote_type_str):
    """
    게시글 또는 댓글에 좋아요/싫어요를 토글합니다.
    vote_type_str: 'like' 또는 'dislike'
    """
    try:
        content_type = ContentType.objects.get_for_id(content_type_id)
        target_model = content_type.model_class()
        target_object = get_object_or_404(target_model, pk=object_id)
    except ContentType.DoesNotExist:
        return Response({"error": "잘못된 컨텐츠 타입입니다."}, status=status.HTTP_400_BAD_REQUEST)

    if vote_type_str.lower() == 'like':
        vote_type = LikeDislike.LIKE
    elif vote_type_str.lower() == 'dislike':
        vote_type = LikeDislike.DISLIKE
    else:
        return Response({"error": "잘못된 투표 타입입니다. ('like' 또는 'dislike')"}, status=status.HTTP_400_BAD_REQUEST)

    existing_vote = LikeDislike.objects.filter(
        user=request.user, content_type=content_type, object_id=object_id
    ).first()

    if existing_vote:
        if existing_vote.vote_type == vote_type:  # 같은 투표: 취소 (삭제)
            existing_vote.delete()
            return Response({"status": "vote_cancelled"}, status=status.HTTP_200_OK)
        else:  # 다른 투표: 변경 (업데이트)
            existing_vote.vote_type = vote_type
            existing_vote.save()
            serializer = LikeDislikeSerializer(existing_vote)
            return Response(serializer.data, status=status.HTTP_200_OK)
    else:  # 새 투표: 생성
        new_vote = LikeDislike.objects.create(
            user=request.user,
            content_type=content_type,
            object_id=object_id,
            vote_type=vote_type
        )
        serializer = LikeDislikeSerializer(new_vote)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# --- User Search and Profile API Views ---
class UserSearchAPIView(generics.ListAPIView):
    """사용자 검색 (닉네임 또는 아이디)"""
    queryset = User.objects.all()
    serializer_class = AuthorDisplaySerializer  # 간단한 정보만 표시
    permission_classes = [permissions.AllowAny]  # 누구나 검색 가능
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'nickname']  # User 모델에 nickname 필드 가정


class UserProfileAPIView(generics.RetrieveAPIView):
    """사용자 프로필 상세 조회"""
    queryset = User.objects.prefetch_related(
        'following_set',  # 내가 팔로우 하는 사람들
        'follower_set',  # 나를 팔로우 하는 사람들
        # 'board_posts', 
        # 'board_problems'
    ).all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.AllowAny]  # 누구나 프로필 조회 가능
    lookup_field = 'username'  # URL에서 username으로 사용자 조회 / 또는 'pk'


# --- User Follow API Views ---
class FollowToggleAPIView(generics.GenericAPIView):
    """사용자 팔로우/언팔로우 토글"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserFollowSerializer  # 응답용 (실제 생성은 직접)

    def post(self, request, username_to_follow):
        user_to_follow = get_object_or_404(User, username=username_to_follow)
        follower = request.user

        if follower == user_to_follow:
            return Response({"error": "자기 자신을 팔로우할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        follow_instance, created = UserFollow.objects.get_or_create(
            follower=follower,
            following=user_to_follow
        )

        if not created:  # 이미 존재하면 (get_or_create가 get을 한 경우) -> 언팔로우
            follow_instance.delete()
            return Response({"status": "unfollowed"}, status=status.HTTP_200_OK)
        else:  # 새로 생성된 경우 -> 팔로우 성공
            serializer = self.get_serializer(follow_instance)
            return Response({"status": "followed", "data": serializer.data}, status=status.HTTP_201_CREATED)


class FollowingListAPIView(generics.ListAPIView):
    """특정 사용자가 팔로우하는 사용자 목록"""
    serializer_class = AuthorDisplaySerializer  # 팔로잉하는 사용자들의 간략 프로필
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        # user.following_set.all()은 UserFollow 객체 목록을 반환
        # 이 UserFollow 객체들에서 'following' 필드(User 객체)를 가져와야 함
        return User.objects.filter(follower_set__follower=user)  # UserFollow의 related_name 사용


class FollowersListAPIView(generics.ListAPIView):
    """특정 사용자를 팔로우하는 사용자 목록"""
    serializer_class = AuthorDisplaySerializer  # 팔로워들의 간략 프로필
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        # user.follower_set.all()은 UserFollow 객체 목록을 반환
        # 이 UserFollow 객체들에서 'follower' 필드(User 객체)를 가져와야 함
        return User.objects.filter(following_set__following=user)  # UserFollow의 related_name 사용


# --- Problem API Views ---
class ProblemListCreateAPIView(generics.ListCreateAPIView):
    queryset = Problem.objects.select_related('author').prefetch_related('files', 'choices').all()
    serializer_class = ProblemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # 문제 목록은 누구나, 생성은 로그인 사용자
    parser_classes = [MultiPartParser, FormParser]  # 파일 업로드 지원
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['author__username']
    search_fields = ['title', 'content', 'author__username', 'author__nickname']
    ordering_fields = ['created_at']

    def perform_create(self, serializer):
        # serializer.save(author=self.request.user) # Serializer의 create에서 처리
        serializer.save()


class ProblemDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Problem.objects.select_related('author').prefetch_related('files', 'choices').all()
    serializer_class = ProblemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]  # 수정/삭제는 출제자 또는 관리자
    parser_classes = [MultiPartParser, FormParser]


class UserProblemAttemptCreateAPIView(generics.CreateAPIView):
    """사용자의 문제 풀이 시도 제출"""
    queryset = UserProblemAttempt.objects.all()
    serializer_class = UserProblemAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]  # 로그인한 사용자만 제출 가능

    # perform_create에서 user는 Serializer의 HiddenField로 자동 할당됨
    # is_correct는 모델의 save() 메소드에서 자동 계산됨


class FollowedPostsAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend, filters.SearchFilter]
    # 어노테이트된 필드명으로 변경
    ordering_fields = ['created_at', 'annotated_likes_count', 'annotated_comment_count']

    # default_ordering = ['-created_at'] # 기본 정렬은 Post 모델의 Meta.ordering 또는 OrderingFilter 기본값 따름

    def get_queryset(self):
        user = self.request.user
        users_i_follow = User.objects.filter(follower_set__follower=user)

        queryset = Post.objects.filter(author__in=users_i_follow) \
            .select_related('author') \
            .prefetch_related('files', 'comments', 'likes_dislikes')

        queryset = queryset.annotate(
            # 어노테이션 필드 이름을 모델 프로퍼티와 다르게 지정
            annotated_likes_count=Count('likes_dislikes', filter=Q(likes_dislikes__vote_type=LikeDislike.LIKE),
                                        distinct=True),
            annotated_comment_count=Count('comments', distinct=True)
        )

        # OrderingFilter가 URL 파라미터에 따라 정렬을 처리합니다.
        # 기본 정렬은 Post 모델의 Meta.ordering을 따르도록 하거나, 여기서 명시적으로 .order_by()를 추가할 수 있습니다.
        # 예: return queryset.order_by('-created_at')
        return queryset.all()
