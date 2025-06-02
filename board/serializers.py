from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from .models import Post, PostFile, Comment, LikeDislike, UserFollow, Problem, ProblemFile, ProblemChoice, UserProblemAttempt
import json

User = get_user_model()

class AuthorDisplaySerializer(serializers.ModelSerializer):
    """작성자 정보 Serializer (게시글, 댓글, 문제 등에 사용)"""
    active_title_name = serializers.CharField(source='active_title.name', read_only=True, allow_null=True)
    active_title_color = serializers.SerializerMethodField(read_only=True)
    tier_info = serializers.SerializerMethodField(read_only=True)
    level = serializers.IntegerField(source='current_level', read_only=True, default=1)
    nickname = serializers.CharField(read_only=True, allow_blank=True, allow_null=True)
    profile_image = serializers.ImageField(read_only=True) # <--- 이 줄 추가 (User 모델에 profile_image 필드 존재 가정)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'nickname',
            'profile_image',
            'active_title_name',
            'active_title_color',
            'tier_info',
            'level',
        ]

    def get_active_title_color(self, obj):
        if hasattr(obj, 'active_title') and obj.active_title and hasattr(obj.active_title, 'default_display_color'):
            return obj.active_title.default_display_color
        return '#FFFFFF'

    def get_tier_info(self, obj):
        if hasattr(obj, 'get_tier_info') and callable(obj.get_tier_info):
            tier_data = obj.get_tier_info()
            return {
                'name': tier_data.get('name', '정보 없음'),
                'image': tier_data.get('image', '')
            }
        return {'name': '정보 없음', 'image': ''}


class UserProfileSerializer(AuthorDisplaySerializer):
    """사용자 프로필 상세 정보 Serializer (팔로워/팔로잉 수 포함)"""
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    # User 모델에 bio 필드가 있다고 가정하고 추가 (없다면 User 모델에 추가 필요)
    bio = serializers.CharField(source='bio', read_only=True, allow_blank=True, allow_null=True)
    # 사용자가 작성한 게시글 수 (User 모델에 board_posts related_name이 있다고 가정)
    board_posts_count = serializers.IntegerField(source='board_posts.count', read_only=True)


    class Meta(AuthorDisplaySerializer.Meta):
        fields = AuthorDisplaySerializer.Meta.fields + [
            'follower_count',
            'following_count',
            'bio',
            'board_posts_count',
        ]
        # 만약 User 모델에 bio 필드가 직접 없다면, source를 UserProfile 등으로 변경하거나 해당 필드 제거 필요

    def get_follower_count(self, obj):
        # User 모델의 follower_set (UserFollow 모델의 related_name)을 사용
        return obj.follower_set.count() if hasattr(obj, 'follower_set') else 0

    def get_following_count(self, obj):
        # User 모델의 following_set (UserFollow 모델의 related_name)을 사용
        return obj.following_set.count() if hasattr(obj, 'following_set') else 0


class PostFileSerializer(serializers.ModelSerializer):
    file_url = serializers.FileField(source='file', read_only=True)  # URL 반환을 위해 FileField 사용

    class Meta:
        model = PostFile
        fields = ['id', 'file_url', 'file_type', 'uploaded_at']


class CommentSerializer(serializers.ModelSerializer):
    author_details = AuthorDisplaySerializer(source='author', read_only=True)
    # author_username = serializers.CharField(source='author.username', read_only=True) # author_details.username으로 대체
    replies = serializers.SerializerMethodField(read_only=True)  # 대댓글
    likes_count = serializers.IntegerField(read_only=True, default=0)
    dislikes_count = serializers.IntegerField(read_only=True, default=0)

    # 사용자의 좋아요/싫어요 여부 필드 (선택적)
    # user_vote = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'author_details', 'parent_comment', 'content',
            'created_at', 'updated_at', 'is_anonymous', 'replies',
            'likes_count', 'dislikes_count',  # 'user_vote'
        ]
        read_only_fields = ['author_details', 'created_at', 'updated_at', 'replies', 'likes_count', 'dislikes_count']

    def get_replies(self, obj):
        # 대댓글이 있고, 너무 깊어지지 않도록 1단계만 직렬화 (또는 최대 깊이 설정)
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True, context=self.context).data
        return []

    # def get_user_vote(self, obj):
    #     user = self.context.get('request').user
    #     if user and user.is_authenticated:
    #         try:
    #             like_dislike = LikeDislike.objects.get(
    #                 user=user,
    #                 content_type=ContentType.objects.get_for_model(Comment),
    #                 object_id=obj.pk
    #             )
    #             return like_dislike.vote_type
    #         except LikeDislike.DoesNotExist:
    #             return None
    #     return None

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['author'] = request.user
        # 익명 댓글 처리 (웹 폼과 일관성 있게)
        if not request.user.is_staff and 'is_anonymous' in validated_data:
            pass  # 사용자가 is_anonymous를 직접 설정할 수 있게 함
        return super().create(validated_data)


class PostSerializer(serializers.ModelSerializer):
    author_details = AuthorDisplaySerializer(source='author', read_only=True)
    files = PostFileSerializer(many=True, read_only=True)  # 게시글 파일 목록
    uploaded_files = serializers.ListField(  # 파일 업로드용 (write_only)
        child=serializers.FileField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False  # 파일은 선택 사항
    )
    uploaded_file_types = serializers.ListField(  # 업로드 파일 타입 지정 (write_only)
        child=serializers.ChoiceField(choices=PostFile.FILE_TYPE_CHOICES),
        write_only=True,
        required=False
    )

    comments = CommentSerializer(many=True, read_only=True)  # 댓글 목록 (성능 고려 필요)
    comment_count = serializers.IntegerField(read_only=True, default=0)
    likes_count = serializers.IntegerField(read_only=True, default=0)
    dislikes_count = serializers.IntegerField(read_only=True, default=0)

    # user_vote = serializers.SerializerMethodField() # 사용자의 게시글 좋아요/싫어요 여부

    class Meta:
        model = Post
        fields = [
            'id', 'author_details', 'title', 'content', 'created_at', 'updated_at',
            'is_notice', 'is_pinned', 'title_color', 'is_anonymous',
            'files', 'uploaded_files', 'uploaded_file_types',  # 파일 관련 필드
            'comments', 'comment_count', 'likes_count', 'dislikes_count',  # 'user_vote'
        ]
        # 관리자만 설정 가능한 필드는 API 레벨에서 권한으로 제어하거나, create/update에서 로직으로 처리
        # 일반 사용자는 is_notice, is_pinned, title_color 변경 불가
        read_only_fields = ['author_details', 'created_at', 'updated_at', 'files', 'comments', 'comment_count',
                            'likes_count', 'dislikes_count']

    # def get_user_vote(self, obj):
    #     user = self.context.get('request').user
    #     if user and user.is_authenticated:
    #         try:
    #             like_dislike = LikeDislike.objects.get(
    #                 user=user,
    #                 content_type=ContentType.objects.get_for_model(Post),
    #                 object_id=obj.pk
    #             )
    #             return like_dislike.vote_type
    #         except LikeDislike.DoesNotExist:
    #             return None
    #     return None

    def _handle_admin_fields(self, instance, validated_data, user):
        # 관리자가 아닌 경우, 관리자 전용 필드 변경 시도 막기
        if not user.is_staff:
            validated_data.pop('is_notice', None)
            validated_data.pop('is_pinned', None)
            validated_data.pop('title_color', None)
        elif instance:  # 수정 시, 관리자라도 값이 안 넘어오면 기존 값 유지
            if 'is_notice' not in validated_data: validated_data['is_notice'] = instance.is_notice
            if 'is_pinned' not in validated_data: validated_data['is_pinned'] = instance.is_pinned
            if 'title_color' not in validated_data: validated_data['title_color'] = instance.title_color
        return validated_data

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        uploaded_files_data = validated_data.pop('uploaded_files', [])
        uploaded_file_types_data = validated_data.pop('uploaded_file_types', [])

        # 관리자 필드 처리
        validated_data = self._handle_admin_fields(None, validated_data, user)

        validated_data['author'] = user
        post = super().create(validated_data)

        # 파일 처리
        for i, file_data in enumerate(uploaded_files_data):
            file_type = uploaded_file_types_data[i] if i < len(uploaded_file_types_data) else 'IMAGE'  # 기본값 이미지
            PostFile.objects.create(post=post, file=file_data, file_type=file_type)

        return post

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = request.user

        # 파일 관련 필드는 현재 Serializer에서는 직접 수정 지원 안 함 (별도 엔드포인트나 복잡한 로직 필요)
        # 여기서는 텍스트 필드 위주 업데이트
        validated_data.pop('uploaded_files', None)
        validated_data.pop('uploaded_file_types', None)

        # 관리자 필드 처리
        validated_data = self._handle_admin_fields(instance, validated_data, user)

        return super().update(instance, validated_data)


class LikeDislikeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())  # 현재 사용자 자동 할당

    class Meta:
        model = LikeDislike
        fields = ['id', 'user', 'vote_type', 'content_type', 'object_id', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, data):
        user = data['user']
        content_type = data['content_type']
        object_id = data['object_id']

        # content_type이 Post 또는 Comment인지 확인 (필요 시 확장)
        allowed_models = (Post, Comment)
        if not issubclass(content_type.model_class(), allowed_models):
            raise serializers.ValidationError("좋아요/싫어요는 게시글 또는 댓글에만 가능합니다.")

        # 기존 투표 확인 (업데이트 또는 생성 분기)
        existing_vote = LikeDislike.objects.filter(
            user=user, content_type=content_type, object_id=object_id
        ).first()

        if existing_vote:
            # 같은 투표를 다시 누르면 취소 (삭제)
            if existing_vote.vote_type == data['vote_type']:
                # 이 Serializer는 생성/업데이트 용이므로, 취소는 뷰에서 처리하거나 별도 액션 필요
                # 여기서는 에러 대신 기존 투표를 반환하거나, 업데이트 로직을 넣을 수 있음
                # raise serializers.ValidationError({"detail": "이미 같은 유형으로 투표했습니다. 취소하려면 다른 API를 사용하세요."})
                pass  # 뷰에서 처리하도록 함 (삭제 또는 업데이트)
            else:  # 다른 유형으로 투표하면 변경 (업데이트)
                existing_vote.vote_type = data['vote_type']
                existing_vote.save()
                # 업데이트된 객체를 반환하기 위해 validated_data를 업데이트
                data['id'] = existing_vote.id
        return data


class UserFollowSerializer(serializers.ModelSerializer):
    follower = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # following = UserProfileSerializer(read_only=True) # 팔로잉하는 사용자 정보 표시
    following_username = serializers.CharField(write_only=True, help_text="팔로우할 사용자의 username")

    class Meta:
        model = UserFollow
        fields = ['id', 'follower', 'following', 'following_username', 'created_at']
        read_only_fields = ['created_at', 'following']  # following은 username으로 받아서 내부 처리

    def validate_following_username(self, username):
        try:
            user_to_follow = User.objects.get(username=username)
            return user_to_follow
        except User.DoesNotExist:
            raise serializers.ValidationError("존재하지 않는 사용자입니다.")

    def create(self, validated_data):
        follower = validated_data['follower']
        following_user = validated_data.pop('following_username')  # username으로 받은 User 객체

        if follower == following_user:
            raise serializers.ValidationError("자기 자신을 팔로우할 수 없습니다.")

        # 이미 팔로우 중인지 확인
        if UserFollow.objects.filter(follower=follower, following=following_user).exists():
            raise serializers.ValidationError("이미 팔로우하고 있는 사용자입니다.")

        return UserFollow.objects.create(follower=follower, following=following_user)


class ProblemFileSerializer(serializers.ModelSerializer):
    file_url = serializers.FileField(source='file', read_only=True)

    class Meta:
        model = ProblemFile
        fields = ['id', 'file_url', 'file_type', 'uploaded_at']


class ProblemChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemChoice
        fields = ['id', 'problem', 'choice_text', 'is_correct']
        # 문제 생성/수정 시 problem 필드는 자동으로 채워지거나 context에서 가져오도록 처리 가능
        # 여기서는 생성 시 problem ID를 직접 받도록 함 (또는 Nested writable serializer)
        extra_kwargs = {
            'problem': {'write_only': True, 'required': False}  # 문제 생성 시 내부적으로 설정
        }


class ProblemSerializer(serializers.ModelSerializer):
    author_details = AuthorDisplaySerializer(source='author', read_only=True)
    # 출력용: choices 필드는 ProblemChoiceSerializer를 통해 객체 리스트로 표현
    choices_display = ProblemChoiceSerializer(source='choices', many=True, read_only=True)
    # 입력용: multipart/form-data로 받을 때 JSON 문자열로 받기 위한 필드
    choices_input = serializers.CharField(write_only=True, help_text="객관식 보기들의 JSON 배열 문자열")

    files = ProblemFileSerializer(many=True, read_only=True)  # 문제 파일 목록 (출력용)
    uploaded_files = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False  # 파일은 선택 사항
    )
    uploaded_file_types = serializers.ListField(
        child=serializers.ChoiceField(choices=ProblemFile.FILE_TYPE_CHOICES),
        write_only=True,
        required=False  # 파일 타입도 선택 사항 (파일이 있을 경우에만 유효)
    )

    class Meta:
        model = Problem
        fields = [
            'id', 'author_details', 'title', 'content',
            'created_at', 'updated_at',
            'choices_display',  # GET 요청 시 사용될 필드명
            'choices_input',  # POST/PUT 요청 시 사용될 필드명 (form-data 내 JSON 문자열)
            'files', 'uploaded_files', 'uploaded_file_types'
        ]
        read_only_fields = ['author_details', 'created_at', 'updated_at', 'files', 'choices_display']

    def create(self, validated_data):
        request = self.context.get('request')

        # choices_input (JSON 문자열)을 파싱하여 choices_data (Python 리스트)로 변환
        choices_json_string = validated_data.pop('choices_input')
        try:
            choices_data = json.loads(choices_json_string)
            if not isinstance(choices_data, list):
                raise serializers.ValidationError({"choices_input": "보기는 JSON 배열 형태여야 합니다."})
            for choice_item in choices_data:  # 각 보기 항목 유효성 검사 (간단히)
                if not isinstance(choice_item,
                                  dict) or 'choice_text' not in choice_item or 'is_correct' not in choice_item:
                    raise serializers.ValidationError({"choices_input": "각 보기는 'choice_text'와 'is_correct'를 포함해야 합니다."})
        except json.JSONDecodeError:
            raise serializers.ValidationError({"choices_input": "잘못된 JSON 형식의 보기 문자열입니다."})
        except TypeError:  # json.loads에 None 등이 들어갈 경우
            raise serializers.ValidationError({"choices_input": "보기 정보가 필요합니다."})

        uploaded_files_data = validated_data.pop('uploaded_files', [])
        uploaded_file_types_data = validated_data.pop('uploaded_file_types', [])

        validated_data['author'] = request.user
        problem = Problem.objects.create(**validated_data)

        for choice_data_item in choices_data:
            ProblemChoice.objects.create(problem=problem, **choice_data_item)

        for i, file_data in enumerate(uploaded_files_data):
            file_type = uploaded_file_types_data[i] if i < len(uploaded_file_types_data) else 'IMAGE'
            ProblemFile.objects.create(problem=problem, file=file_data, file_type=file_type)

        return problem

    def update(self, instance, validated_data):
        choices_json_string = validated_data.pop('choices_input', None)
        if choices_json_string is not None:
            try:
                choices_data = json.loads(choices_json_string)
                if not isinstance(choices_data, list):
                    raise serializers.ValidationError({"choices_input": "보기는 JSON 배열 형태여야 합니다."})
                for choice_item in choices_data:  # 각 보기 항목 유효성 검사 (간단히)
                    if not isinstance(choice_item,
                                      dict) or 'choice_text' not in choice_item or 'is_correct' not in choice_item:
                        raise serializers.ValidationError(
                            {"choices_input": "각 보기는 'choice_text'와 'is_correct'를 포함해야 합니다."})

                # 기존 보기 삭제 후 새로 생성 (간단한 방식)
                instance.choices.all().delete()
                for choice_data_item in choices_data:
                    ProblemChoice.objects.create(problem=instance, **choice_data_item)
            except json.JSONDecodeError:
                raise serializers.ValidationError({"choices_input": "잘못된 JSON 형식의 보기 문자열입니다."})
            except TypeError:
                raise serializers.ValidationError({"choices_input": "보기 정보가 필요합니다."})

        # 나머지 필드 업데이트
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        # TODO: 파일 업데이트 로직 추가 필요 (uploaded_files, uploaded_file_types 처리)
        instance.save()
        return instance


class UserProblemAttemptSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    # problem_title = serializers.CharField(source='problem.title', read_only=True)
    # selected_choice_text = serializers.CharField(source='selected_choice.choice_text', read_only=True)

    class Meta:
        model = UserProblemAttempt
        fields = [
            'id', 'user', 'problem', 'selected_choice',
            'is_correct', 'attempted_at'
        ]
        read_only_fields = ['is_correct', 'attempted_at']

    def validate(self, data):
        user = data['user']
        problem = data['problem']
        selected_choice = data['selected_choice']

        if selected_choice.problem != problem:
            raise serializers.ValidationError("선택한 보기가 해당 문제의 보기가 아닙니다.")

        # 이미 풀이한 문제인지 확인 (unique_together로 처리되지만, 더 친절한 메시지)
        if UserProblemAttempt.objects.filter(user=user, problem=problem).exists():
            # 수정 불가 정책이라면 에러. 재시도 허용이면 다른 로직.
            raise serializers.ValidationError("이미 이 문제를 풀었습니다.")

        return data