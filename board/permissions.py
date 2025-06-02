from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    객체의 소유자만 수정/삭제 가능, 그 외에는 읽기만 가능.
    관리자(is_staff)는 항상 모든 권한을 가짐.
    """
    def has_object_permission(self, request, view, obj):
        # 읽기 요청(GET, HEAD, OPTIONS)은 항상 허용
        if request.method in permissions.SAFE_METHODS:
            return True

        # 쓰기 요청의 경우, 관리자이거나 객체의 소유자인지 확인
        # obj에 'author' 필드가 있다고 가정
        return request.user.is_staff or (hasattr(obj, 'author') and obj.author == request.user)

class IsStaffOrReadOnly(permissions.BasePermission):
    """
    관리자(is_staff)만 POST, PUT, PATCH, DELETE 가능. 그 외에는 읽기만 허용.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff