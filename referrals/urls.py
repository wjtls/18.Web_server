# referrals/urls.py
from django.urls import path
from .views import MyReferralInfoView, MyDownlinesView

app_name = 'referrals_api' # URL namespace

urlpatterns = [
    path('my-info/', MyReferralInfoView.as_view(), name='my_referral_info'),
    path('my-downlines/', MyDownlinesView.as_view(), name='my_downlines'),
]