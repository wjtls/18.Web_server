# board/serializers.py
from rest_framework import serializers
from .models import Post
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthorDisplaySerializer(serializers.ModelSerializer):
    active_title_name = serializers.CharField(source='active_title.name', read_only=True, allow_null=True)
    active_title_color = serializers.SerializerMethodField(read_only=True)
    tier_info = serializers.SerializerMethodField(read_only=True)
    level = serializers.IntegerField(source='current_level', read_only=True) # User 모델에 current_level 프로퍼티가 있다고 가정
    # nickname 필드는 User 모델에 정의되어 있다고 가정

    class Meta:
        model = User
        fields = [
            'id',
            'username', # ID로 사용 (닉네임 없을 시 대비)
            'nickname', # User 모델에 nickname 필드 필요
            'active_title_name',
            'active_title_color',
            'tier_info',
            'level',
            # 'profile_image_url' # User 모델에 프로필 이미지 URL 필드가 있다면 추가
        ]

    def get_active_title_color(self, obj):
        # User 모델의 active_title 필드 및 관련 Title 모델에 색상 정보(예: default_display_color)가 있다고 가정
        if obj.active_title and hasattr(obj.active_title, 'default_display_color'):
            return obj.active_title.default_display_color
        return '#FFFFFF' # 기본 색상 (예: 흰색)

    def get_tier_info(self, obj):
        # User 모델에 get_tier_info() 메서드가 있고, {'name': '티어명', 'image': '이모지'} 형태를 반환한다고 가정
        if hasattr(obj, 'get_tier_info') and callable(obj.get_tier_info):
            return obj.get_tier_info()
        return {'name': '정보 없음', 'image': ''} # 기본값

class PostSerializer(serializers.ModelSerializer):
    author_details = AuthorDisplaySerializer(source='author', read_only=True)
    # author_username = serializers.CharField(source='author.username', read_only=True) # author_details.username으로 대체 가능

    class Meta:
        model = Post
        fields = [
            'id',
            'author_details', # 'author'와 'author_username' 대신 이 필드 사용
            'title',
            'content',
            'created_at',
            'updated_at',
            'is_notice',
            'is_pinned',
            'title_color',
            'is_anonymous', # Post 모델에 is_anonymous 필드가 있다고 가정
            # 'comment_count', 'like_count', 'dislike_count' # 이 필드들도 Post 모델에 추가 후 여기에 포함
        ]
        # 'author'는 create 메소드에서 설정되므로 read_only_fields에 명시하지 않아도 됩니다.
        # author_details는 source='author' 이고 AuthorDisplaySerializer가 read_only=True 이므로 자동으로 처리됩니다.

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['author'] = request.user
        # is_anonymous 등 다른 필드도 validated_data에서 가져와 설정 가능
        return super().create(validated_data)











# board/api_views.py (또는 views.py에 API 뷰 추가)
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Post

class PostListCreateAPIView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # 글 목록은 누구나, 작성은 로그인 사용자만
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_notice'] # ?is_notice=true 등으로 필터링 가능
    ordering_fields = ['created_at', 'is_pinned'] # ?ordering=-created_at 등으로 정렬 가능
    # 기본 정렬은 Post 모델의 Meta.ordering 사용

    def perform_create(self, serializer):
        serializer.save(author=self.request.user) # 작성자 자동 할당

class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # 상세 보기/수정/삭제 권한
    # TODO: 수정/삭제는 작성자만 가능하도록 권한 설정 추가 필요 (커스텀 Permission 클래스)