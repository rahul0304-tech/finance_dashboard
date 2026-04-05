from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import User, FinancialRecord
from .serializers import UserSerializer, FinancialRecordSerializer, RoleChangeSerializer, PasswordChangeSerializer
from .permissions import IsAdmin, IsAnalystOrAdmin, IsViewerOrHigher
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

@extend_schema_view(
    list=extend_schema(tags=['Admin']),
    retrieve=extend_schema(tags=['Admin']),
    create=extend_schema(tags=['Admin']),
    update=extend_schema(tags=['Admin']),
    partial_update=extend_schema(tags=['Admin']),
    destroy=extend_schema(tags=['Admin']),
    toggle_active=extend_schema(tags=['Admin']),
    change_role=extend_schema(tags=['Admin']),
    change_password=extend_schema(tags=['Admin']),
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin] 

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        user = self.get_object()
        if user.is_superuser:
            return Response({"detail": "Cannot modify superuser status."}, status=status.HTTP_403_FORBIDDEN)
        
        user.is_active = not user.is_active
        user.save()
        return Response({"status": "User active status toggled", "is_active": user.is_active})

    @action(detail=True, methods=['post'], serializer_class=RoleChangeSerializer)
    def change_role(self, request, pk=None):
        user = self.get_object()
        if user.is_superuser:
            return Response({"detail": "Cannot modify superuser role."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user.role = serializer.validated_data['role']
            user.save()
            return Response({"status": "User role updated", "role": user.role})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], serializer_class=PasswordChangeSerializer)
    def change_password(self, request, pk=None):
        user = self.get_object()
        if user.is_superuser and request.user.id != user.id:
            return Response({"detail": "Cannot modify another superuser's password."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({"status": "Password changed successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema_view(
    list=extend_schema(tags=['Analyst']),
    retrieve=extend_schema(tags=['Analyst']),
    create=extend_schema(tags=['Admin']),
    update=extend_schema(tags=['Admin']),
    partial_update=extend_schema(tags=['Admin']),
    destroy=extend_schema(tags=['Admin'])
)
class FinancialRecordViewSet(viewsets.ModelViewSet):
    queryset = FinancialRecord.objects.all().order_by('-date')
    serializer_class = FinancialRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['transaction_type', 'category', 'date']
    search_fields = ['category', 'notes']
    ordering_fields = ['date', 'amount']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAnalystOrAdmin]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

class DashboardSummaryView(APIView):
    permission_classes = [IsViewerOrHigher]

    @extend_schema(tags=['Viewer'])
    def get(self, request):
        now = timezone.now().date()
        thirty_days_ago = now - timedelta(days=30)
        
        base_qs = FinancialRecord.objects.all()
        
        total_income = base_qs.filter(transaction_type='INCOME').aggregate(total=Sum('amount'))['total'] or 0
        total_expense = base_qs.filter(transaction_type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
        net_balance = total_income - total_expense
        
        recent_activity = FinancialRecordSerializer(
            base_qs.order_by('-date')[:5], many=True
        ).data
        
        category_totals = list(base_qs.values('category', 'transaction_type').annotate(total=Sum('amount'), count=Count('id')).order_by('-total'))
        
        monthly_income = base_qs.filter(transaction_type='INCOME', date__gte=thirty_days_ago).aggregate(total=Sum('amount'))['total'] or 0
        monthly_expense = base_qs.filter(transaction_type='EXPENSE', date__gte=thirty_days_ago).aggregate(total=Sum('amount'))['total'] or 0

        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'net_balance': net_balance,
            'category_totals': category_totals,
            'recent_activity': recent_activity,
            'monthly_trend': {
                'income_last_30_days': monthly_income,
                'expense_last_30_days': monthly_expense
            }
        })

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=['Auth'], request=UserSerializer)
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            response = Response({
                "message": "User registered successfully",
                "access": str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
            
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                samesite='Lax'
            )
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CookieTokenObtainPairView(TokenObtainPairView):
    @extend_schema(tags=['Auth'], request=TokenObtainPairSerializer)
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            refresh_token = response.data.get('refresh')
            if refresh_token:
                response.set_cookie(
                    key='refresh_token',
                    value=refresh_token,
                    httponly=True,
                    samesite='Lax'
                )
                del response.data['refresh']
        return response

class CookieTokenRefreshView(TokenRefreshView):
    @extend_schema(tags=['Auth'], request=TokenRefreshSerializer)
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"detail": "Refresh token missing."}, status=status.HTTP_401_UNAUTHORIZED)

        # Mutate the request data to include the refresh token
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        data['refresh'] = refresh_token
        
        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
