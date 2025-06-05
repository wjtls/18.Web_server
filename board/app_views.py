# board/app_views.py

# 필요한 모듈들을 한 번만 깔끔하게 import 합니다.
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Count
from django.db import transaction

from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from main.views_blockchain import check_and_update_user_subscription #구독확인

# .models에서 필요한 모델들을 import 합니다.
from .models import (
    Post, Comment, LikeDislike, UserFollow, Problem, ProblemChoice,
    UserProblemAttempt, PostFile # PostFile 추가 (PostSerializer에서 사용)
)
# .serializers에서 필요한 Serializer들을 import 합니다.
from .serializers import (
    PostSerializer, CommentSerializer, LikeDislikeSerializer, UserFollowSerializer,
    ProblemSerializer, UserProblemAttemptSerializer, UserProfileSerializer,
    AuthorDisplaySerializer,
    UserSummarySerializer  # <<<--- UserSummarySerializer를 명시적으로 포함!
)
from .permissions import IsOwnerOrReadOnly, IsStaffOrReadOnly

User = get_user_model()

# --- Current User Profile API View ---
class CurrentUserProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic # 트랜잭션으로 감싸기
    def retrieve(self, request, *args, **kwargs):
        try:
            # 요청 시점에서 DB로부터 최신 사용자 정보를 가져오고, 업데이트를 위해 잠금(lock)
            user_instance = User.objects.select_for_update().get(pk=request.user.pk)
        except User.DoesNotExist:
            return Response({"detail": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # --- 구독 만료 체크 ---
        print(f"\n[API VIEW - CurrentUserProfileAPIView (retrieve)] User: '{user_instance.username}' - Attempting subscription check.")
        subscription_updated = check_and_update_user_subscription(user_instance) # 내부에서 DB 저장 발생 가능

        if subscription_updated:
            # check_and_update_user_subscription 함수 내에서 DB가 변경되었으므로,
            # 현재 user_instance 객체도 DB와 동일한 최신 상태를 갖도록 refresh
            user_instance.refresh_from_db()
            print(f"[API VIEW - CurrentUserProfileAPIView (retrieve)] User: '{user_instance.username}' - Subscription was updated by check. Plan after refresh: '{user_instance.subscription_plan}'")
        else:
            # 이미 FREE이거나, 아직 만료되지 않은 경우 등 DB 변경이 없었던 경우
            print(f"[API VIEW - CurrentUserProfileAPIView (retrieve)] User: '{user_instance.username}' - Subscription was NOT updated by check.")
        # --- 구독 만료 체크 종료 ---

        # 최종적으로 (업데이트되었을 수도 있는) user_instance를 직렬화하여 반환
        serializer = self.get_serializer(user_instance)
        return Response(serializer.data)

# --- Post API Views ---
class PostListCreateAPIView(generics.ListCreateAPIView):
    # ... (이하 기존 PostListCreateAPIView 코드와 동일하게 유지)
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['is_notice', 'author__username', 'is_anonymous']
    search_fields = ['title', 'content', 'author__username', 'author__nickname']
    ordering_fields = ['created_at', 'is_pinned', 'annotated_likes_count', 'annotated_comment_count']

    def get_queryset(self):
        queryset = Post.objects.select_related('author').prefetch_related('files', 'comments', 'likes_dislikes')
        queryset = queryset.annotate(
            annotated_likes_count=Count('likes_dislikes', filter=Q(likes_dislikes__vote_type=LikeDislike.LIKE), distinct=True),
            annotated_comment_count=Count('comments', distinct=True)
        )
        return queryset.all()

    def perform_create(self, serializer):
        serializer.save() # PostSerializer의 create에서 author 처리 가정

class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    # ... (이하 기존 PostDetailAPIView 코드와 동일하게 유지)
    queryset = Post.objects.select_related('author').prefetch_related('files', 'comments', 'likes_dislikes').all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]


# --- Comment API Views ---
class CommentListCreateAPIView(generics.ListCreateAPIView):
    # ... (이하 기존 CommentListCreateAPIView 코드와 동일하게 유지)
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def get_queryset(self):
        post_pk = self.kwargs.get('post_pk')
        post = get_object_or_404(Post, pk=post_pk)
        return Comment.objects.filter(post=post, parent_comment=None).select_related('author').prefetch_related('replies', 'likes_dislikes').all()
    def perform_create(self, serializer):
        post_pk = self.kwargs.get('post_pk')
        post = get_object_or_404(Post, pk=post_pk)
        serializer.save(post=post)

class CommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    # ... (이하 기존 CommentDetailAPIView 코드와 동일하게 유지)
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    def get_queryset(self):
        post_pk = self.kwargs.get('post_pk')
        return Comment.objects.filter(post_id=post_pk).select_related('author').prefetch_related('replies','likes_dislikes').all()

# --- Like/Dislike API View ---
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def vote_content_object(request, content_type_id, object_id, vote_type_str):
    # ... (이하 기존 vote_content_object 코드와 동일하게 유지)
    try:
        content_type = ContentType.objects.get_for_id(content_type_id)
        target_model = content_type.model_class()
        target_object = get_object_or_404(target_model, pk=object_id)
    except ContentType.DoesNotExist:
        return Response({"error": "잘못된 컨텐츠 타입입니다."}, status=status.HTTP_400_BAD_REQUEST)
    if vote_type_str.lower() == 'like': vote_type = LikeDislike.LIKE
    elif vote_type_str.lower() == 'dislike': vote_type = LikeDislike.DISLIKE
    else: return Response({"error": "잘못된 투표 타입입니다. ('like' 또는 'dislike')"}, status=status.HTTP_400_BAD_REQUEST)
    existing_vote = LikeDislike.objects.filter(user=request.user, content_type=content_type, object_id=object_id).first()
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            existing_vote.delete()
            return Response({"status": "vote_cancelled"}, status=status.HTTP_200_OK)
        else:
            existing_vote.vote_type = vote_type
            existing_vote.save()
            serializer = LikeDislikeSerializer(existing_vote)
            return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        new_vote = LikeDislike.objects.create(user=request.user, content_type=content_type, object_id=object_id, vote_type=vote_type)
        serializer = LikeDislikeSerializer(new_vote)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# --- User Search and Other User Profile API Views ---
class UserSearchAPIView(generics.ListAPIView):
    # ... (이하 기존 UserSearchAPIView 코드와 동일하게 유지)
    queryset = User.objects.all()
    serializer_class = AuthorDisplaySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'nickname']

    def get_queryset(self):
        return User.objects.filter(is_active=True)
    def get_serializer_context(self):
        """
        Serializer에게 request 객체를 context로 전달
        """
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


# --- UserListAPIView (사용자 목록 - 추천 등) ---
class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.filter(is_active=True).order_by('-date_joined')
    serializer_class = AuthorDisplaySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    ordering_fields = ['date_joined', 'username']  # 예시: 필요한 경우 정렬 필드 지정
    search_fields = ['username', 'nickname'] # 예시: UserListAPIView에서도 검색을 지원한다면
    def get_serializer_context(self):
        """
        Serializer에게 request 객체를 context로 전달합니다.
        """
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

class UserProfileAPIView(generics.RetrieveAPIView): # 다른 사용자 프로필 조회용
    # ... (이하 기존 UserProfileAPIView 코드와 동일하게 유지)
    queryset = User.objects.prefetch_related('following_set','follower_set').all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'username'

# --- User Follow API Views ---
class FollowToggleAPIView(generics.GenericAPIView):
    """사용자 팔로우/언팔로우 토글"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserFollowSerializer  # <<<--- serializer_class 정의!

    def post(self, request, username_to_follow):
        user_to_follow = get_object_or_404(User, username=username_to_follow)
        follower = request.user

        if follower == user_to_follow:
            return Response({"error": "자기 자신을 팔로우할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            follow_instance = UserFollow.objects.filter(follower=follower, following=user_to_follow).first()

            if follow_instance:
                # 이미 팔로우 중이므로 언팔로우
                follow_instance.delete()
                return Response({"status": "unfollowed"}, status=status.HTTP_200_OK)
            else:
                # 팔로우 관계 생성
                # UserFollowSerializer의 create 메소드에서 follower는 자동으로 현재 유저로 설정될 수 있으므로,
                # 여기서는 following 정보만 전달해도 될 수 있습니다. (Serializer 구현에 따라 다름)
                # 현재 UserFollowSerializer는 following_username을 받아서 처리하므로,
                # 직접 UserFollow.objects.create를 사용하는 것이 더 명확할 수 있습니다.
                new_follow = UserFollow.objects.create(follower=follower, following=user_to_follow)
                # 생성된 인스턴스를 응답으로 보내기 위해 serializer 사용
                serializer = self.get_serializer(new_follow)
                return Response({"status": "followed", "data": serializer.data}, status=status.HTTP_201_CREATED)
        except IntegrityError:
            # 이 경우는 거의 발생하지 않아야 하지만, 혹시 모를 동시성 문제로 create 시점에 이미 레코드가 생긴 경우
            return Response({"error": "팔로우 처리 중 데이터 충돌이 발생했습니다. 다시 시도해주세요."}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            # 기타 예외 처리
            return Response({"error": f"오류 발생: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FollowingListAPIView(generics.ListAPIView):
    serializer_class = UserSummarySerializer # UserSummarySerializer 사용 (이제 import 됨)
    permission_classes = [permissions.AllowAny] # 또는 IsAuthenticated

    def get_queryset(self):
        username = self.kwargs.get('username')
        target_user = get_object_or_404(User, username=username)
        # UserFollow 모델에서 follower 필드가 target_user인 UserFollow 객체들을 찾고,
        # 그 객체들의 'following' 필드 (User 객체)들을 반환합니다.
        # UserFollow.follower의 related_name이 'following_set'이고 UserFollow.following의 related_name이 'follower_set'인 경우
        # return User.objects.filter(follower_set__follower=target_user)
        # 또는 UserFollow 모델을 직접 쿼리:
        following_relations = UserFollow.objects.filter(follower=target_user).select_related('following')
        return [relation.following for relation in following_relations]


class FollowersListAPIView(generics.ListAPIView):
    serializer_class = UserSummarySerializer # UserSummarySerializer 사용 (이제 import 됨)
    permission_classes = [permissions.AllowAny] # 또는 IsAuthenticated

    def get_queryset(self):
        username = self.kwargs.get('username')
        target_user = get_object_or_404(User, username=username)
        # UserFollow 모델에서 following 필드가 target_user인 UserFollow 객체들을 찾고,
        # 그 객체들의 'follower' 필드 (User 객체)들을 반환합니다.
        # return User.objects.filter(following_set__following=target_user)
        # 또는 UserFollow 모델을 직접 쿼리:
        follower_relations = UserFollow.objects.filter(following=target_user).select_related('follower')
        return [relation.follower for relation in follower_relations]

# --- Problem API Views ---
class ProblemListCreateAPIView(generics.ListCreateAPIView):
    # ... (이하 기존 ProblemListCreateAPIView 코드와 동일하게 유지)
    queryset = Problem.objects.select_related('author').prefetch_related('files', 'choices').all()
    serializer_class = ProblemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['author__username']
    search_fields = ['title', 'content', 'author__username', 'author__nickname']
    ordering_fields = ['created_at']
    def perform_create(self, serializer):
        serializer.save()

class ProblemDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    # ... (이하 기존 ProblemDetailAPIView 코드와 동일하게 유지)
    queryset = Problem.objects.select_related('author').prefetch_related('files', 'choices').all()
    serializer_class = ProblemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

class UserProblemAttemptCreateAPIView(generics.CreateAPIView):
    # ... (이하 기존 UserProblemAttemptCreateAPIView 코드와 동일하게 유지)
    queryset = UserProblemAttempt.objects.all()
    serializer_class = UserProblemAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

# --- Followed Posts API View ---
class FollowedPostsAPIView(generics.ListAPIView):
    # ... (이하 기존 FollowedPostsAPIView 코드와 동일하게 유지)
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend, filters.SearchFilter]
    ordering_fields = ['created_at', 'annotated_likes_count', 'annotated_comment_count']
    def get_queryset(self):
        user = self.request.user
        users_i_follow_relations = UserFollow.objects.filter(follower=user)
        users_i_follow_qs = User.objects.filter(pk__in=users_i_follow_relations.values_list('following_id', flat=True))
        queryset = Post.objects.filter(author__in=users_i_follow_qs).select_related('author').prefetch_related('files', 'comments', 'likes_dislikes')
        queryset = queryset.annotate(
            annotated_likes_count=Count('likes_dislikes', filter=Q(likes_dislikes__vote_type=LikeDislike.LIKE), distinct=True),
            annotated_comment_count=Count('comments', distinct=True)
        )
        return queryset.all()