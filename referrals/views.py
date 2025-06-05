# referrals/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

# User 모델을 가져오는 방법 (serializers.py와 동일한 방식 사용)
# 1. User 모델이 main 앱에 있다면 (가정):
from main.models import User
# 2. Django의 권장 방식:
# from django.contrib.auth import get_user_model
# User = get_user_model()

from .serializers import MyReferralInfoSerializer, ReferredUserSerializer


class MyReferralInfoView(APIView):
    """
    GET /api/v1/referrals/my-info/
    현재 로그인한 사용자의 추천 관련 정보 반환.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        data_for_serializer = {
            'my_referral_code': user.referral_code,
            'upline_referrer': user.referred_by,
        }

        serializer = MyReferralInfoSerializer(instance=data_for_serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyDownlinesView(APIView):
    """
    GET /api/v1/referrals/my-downlines/
    현재 로그인한 사용자가 추천한 사용자 목록 반환.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        downlines = user.referred_users.all().order_by('-date_joined')  # User 모델의 related_name 사용

        # 페이지네이션 로직 (필요한 경우 주석 해제 및 설정)
        # from rest_framework.pagination import PageNumberPagination
        # paginator = PageNumberPagination()
        # paginator.page_size = 10
        # page = paginator.paginate_queryset(downlines, request, view=self)
        # if page is not None:
        #     serializer = ReferredUserSerializer(page, many=True)
        #     return paginator.get_paginated_response(serializer.data)

        serializer = ReferredUserSerializer(downlines, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)