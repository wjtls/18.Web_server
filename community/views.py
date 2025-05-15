# community/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Post
from .forms import PostForm


# from django.views.decorators.http import require_POST # POST 요청만 받도록 제한 (좋아요 등)

def community_feed_view(request):
    # 모든 게시물을 가져오거나, 팔로우하는 사람들의 게시물만 가져오는 로직 등
    posts = Post.objects.all()  # 일단 모든 게시물

    # 게시물 작성 폼 (로그인한 사용자에게만)
    post_form = PostForm() if request.user.is_authenticated else None

    context = {
        'posts': posts,
        'post_form': post_form,  # 모달에서 사용할 수 있도록 전달 (선택적)
    }
    return render(request, 'main/index5_community.html', context)


@login_required  # 로그인해야 게시물 작성 가능
def create_post_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            # 성공 메시지 추가 가능
            return redirect('community:community_feed')  # 성공 후 피드 페이지로 (네임스페이스 사용 가정)
    else:
        form = PostForm()  # GET 요청 시 빈 폼

    # 만약 모달이 아닌 별도 페이지로 폼을 보여준다면 이 템플릿 렌더링
    # return render(request, 'community/create_post_form.html', {'form': form})
    # 지금은 모달에서 바로 POST 처리 후 리디렉션하는 것으로 가정
    return redirect('community:community_feed')  # GET 요청으로 직접 접근 시 피드로 돌려보냄


@login_required
# @require_POST # 좋아요는 POST 요청으로만 받는 것이 좋음
def like_post_view(request, post_id):
    # AJAX 요청인지 확인 (선택적이지만, JS에서 fetch/AJAX로 호출할 것이므로)
    # if request.headers.get('x-requested-with') == 'XMLHttpRequest':
    if request.method == 'POST':  # POST 요청으로 변경 권장
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        is_liked_by_user = False
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            is_liked_by_user = False
        else:
            post.likes.add(user)
            is_liked_by_user = True

        return JsonResponse({
            'status': 'ok',
            'likes_count': post.likes.count(),
            'is_liked': is_liked_by_user
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# user_profile_view, post_detail_view, add_comment_view 등도 여기에 만들어야 함 (이전 답변 참고)
# 예시: user_profile_view
from django.contrib.auth import get_user_model

User = get_user_model()


def user_profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=profile_user)
    context = {
        'profile_user': profile_user,
        'user_posts': user_posts,
    }
    return render(request, 'community/user_profile.html', context)  # 프로필 템플릿 필요

# ... (다른 뷰들: 게시물 상세, 댓글 추가 등) ...