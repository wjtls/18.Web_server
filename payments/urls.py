from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('add-card/', views.add_card_view, name='add_card'),
    path('card-registration-success/', views.card_registration_success_view, name='card_registration_success'),
    path('create-subscription/', views.create_subscription_view, name='create_subscription'),
    path('charge-item-card/', views.charge_item_card_view, name='charge_item_card'),
]