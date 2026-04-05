from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, FinancialRecordViewSet, DashboardSummaryView,
    RegisterView, CookieTokenObtainPairView, CookieTokenRefreshView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'records', FinancialRecordViewSet, basename='record')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
]
