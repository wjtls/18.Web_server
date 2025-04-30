# board/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required # 관리자 확인용
from django.contrib import messages
from django.http import HttpResponseForbidden # 권한 없음 응답
from .models import Post
from .forms import PostForm, AdminPostForm

# 1. 게시글 목록 보기
def post_list(request):
    """게시글 목록을 보여주는 뷰"""
    # is_notice=True 인 글(공지)과 아닌 글 분리 또는 한번에 정렬
    # 여기서는 Meta ordering 사용: 상단고정 -> 최신순
    posts = Post.objects.all()
    context = {'posts': posts}
    return render(request, 'board/post_list.html', context)

# 2. 게시글 상세 보기
def post_detail(request, pk):
    """개별 게시글 상세 내용을 보여주는 뷰"""
    post = get_object_or_404(Post, pk=pk)
    context = {'post': post}
    return render(request, 'board/post_detail.html', context)

# 3. 새 글 작성
@login_required # 로그인 필수
def post_create(request):
    """새 게시글을 작성하는 뷰 (로그인 사용자)"""
    if request.method == 'POST':
        # 사용자가 관리자인지 확인하여 적절한 폼 사용
        if request.user.is_staff: # is_staff 또는 is_superuser 확인
            form = AdminPostForm(request.POST)
        else:
            form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False) # DB 저장 보류
            post.author = request.user      # 작성자 설정
            # 관리자가 아니면 공지, 고정, 색상 옵션 강제 해제 (보안)
            if not request.user.is_staff:
                post.is_notice = False
                post.is_pinned = False
                post.title_color = 'BLACK'
            post.save() # 최종 DB 저장
            messages.success(request, '새 글이 성공적으로 작성되었습니다.')
            return redirect('board:post_detail', pk=post.pk) # 작성된 글로 이동
        else:
            # 폼 유효성 검사 실패 시
            messages.error(request, '글 작성에 실패했습니다. 입력 내용을 확인해주세요.')
    else:
        # GET 요청 시: 빈 폼 보여주기
        if request.user.is_staff:
            form = AdminPostForm()
        else:
            form = PostForm()

    context = {'form': form, 'is_new': True} # is_new 플래그 추가 (템플릿에서 구분용)
    return render(request, 'board/post_form.html', context)

# 4. 글 수정
@login_required
def post_edit(request, pk):
    """기존 게시글을 수정하는 뷰"""
    post = get_object_or_404(Post, pk=pk)

    # 권한 확인: 작성자 본인 또는 관리자만 수정 가능
    if not (request.user == post.author or request.user.is_staff):
        messages.error(request, '글을 수정할 권한이 없습니다.')
        return redirect('board:post_detail', pk=post.pk)
        # 또는 return HttpResponseForbidden("수정 권한이 없습니다.")

    if request.method == 'POST':
        # 관리자 여부에 따라 다른 폼 사용
        if request.user.is_staff:
            form = AdminPostForm(request.POST, instance=post)
        else:
            form = PostForm(request.POST, instance=post) # 일반 사용자는 제한된 필드 폼

        if form.is_valid():
            edited_post = form.save(commit=False)
            # 관리자가 아니면 관리자 옵션 변경 불가 처리 (이중 보안)
            if not request.user.is_staff:
                edited_post.is_notice = post.is_notice # 원래 값 유지
                edited_post.is_pinned = post.is_pinned
                edited_post.title_color = post.title_color
            edited_post.save()
            messages.success(request, '글이 성공적으로 수정되었습니다.')
            return redirect('board:post_detail', pk=post.pk)
        else:
            messages.error(request, '글 수정에 실패했습니다. 입력 내용을 확인해주세요.')
    else:
        # GET 요청 시: 기존 내용 채워진 폼 보여주기
        if request.user.is_staff:
            form = AdminPostForm(instance=post)
        else:
            form = PostForm(instance=post)

    context = {'form': form, 'post': post, 'is_new': False}
    return render(request, 'board/post_form.html', context)

# 5. 글 삭제
@login_required
def post_delete(request, pk):
    """게시글을 삭제하는 뷰"""
    post = get_object_or_404(Post, pk=pk)

    # 권한 확인: 작성자 본인 또는 관리자만 삭제 가능
    if not (request.user == post.author or request.user.is_staff):
        messages.error(request, '글을 삭제할 권한이 없습니다.')
        return redirect('board:post_detail', pk=post.pk)
        # 또는 return HttpResponseForbidden("삭제 권한이 없습니다.")

    if request.method == 'POST': # 삭제 확인 후 POST 요청
        post_title = post.title # 삭제 메시지용 제목 저장
        post.delete()
        messages.success(request, f'"{post_title}" 글이 삭제되었습니다.')
        return redirect('board:post_list') # 목록으로 이동
    else:
        # GET 요청 시: 삭제 확인 페이지 보여주기
        context = {'post': post}
        return render(request, 'board/post_confirm_delete.html', context)