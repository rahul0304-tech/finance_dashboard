from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, FinancialRecord
from decimal import Decimal
from django.utils import timezone

class FinanceDashboardTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='password', role='ADMIN')
        self.analyst = User.objects.create_user(username='analyst', password='password', role='ANALYST')
        self.viewer = User.objects.create_user(username='viewer', password='password', role='VIEWER')
        
        self.today = timezone.now().date()
        
        self.record1 = FinancialRecord.objects.create(
            amount=Decimal('100.00'), transaction_type='INCOME', category='Salary', date=self.today
        )
        self.record2 = FinancialRecord.objects.create(
            amount=Decimal('50.00'), transaction_type='EXPENSE', category='Groceries', date=self.today
        )

    def authenticate_as(self, user):
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': user.username,
            'password': 'password'
        })
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])

    def test_viewer_access(self):
        self.authenticate_as(self.viewer)
        response = self.client.get(reverse('record-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        response = self.client.get(reverse('dashboard-summary'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_income'], Decimal('100.00'))

    def test_analyst_access(self):
        self.authenticate_as(self.analyst)
        response = self.client.get(reverse('record-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        response = self.client.delete(reverse('record-detail', args=[self.record1.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_access_and_soft_delete(self):
        self.authenticate_as(self.admin)
        response = self.client.delete(reverse('record-detail', args=[self.record1.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.record1.refresh_from_db()
        self.assertTrue(self.record1.is_deleted)
        
        response = self.client.get(reverse('record-list'))
        self.assertEqual(response.data['count'], 1)

    def test_dashboard_aggregations(self):
        self.authenticate_as(self.admin)
        response = self.client.get(reverse('dashboard-summary'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['net_balance'], Decimal('50.00'))

    def test_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password': 'JWT',
            'email': 'newuser@example.com',
            'role': 'VIEWER'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='newuser')
        self.assertEqual(user.role, 'VIEWER')
        self.assertTrue(user.check_password('JWT'))

    def test_cookie_auth(self):
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'admin',
            'password': 'password'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertNotIn('refresh', response.data)
        self.assertIn('refresh_token', response.cookies)
        
        # Test Refresh via Cookie
        self.client.cookies['refresh_token'] = response.cookies['refresh_token'].value
        refresh_response = self.client.post(reverse('token_refresh'))
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

    def test_admin_explicit_endpoints(self):
        self.authenticate_as(self.admin)
        
        # Test change_role
        response = self.client.post(reverse('user-change-role', args=[self.viewer.id]), {
            'role': 'ANALYST'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.viewer.refresh_from_db()
        self.assertEqual(self.viewer.role, 'ANALYST')
        
        # Test toggle_active
        response = self.client.post(reverse('user-toggle-active', args=[self.viewer.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.viewer.refresh_from_db()
        self.assertFalse(self.viewer.is_active)
        
        # Test change_password
        response = self.client.post(reverse('user-change-password', args=[self.viewer.id]), {
            'password': 'newpassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.viewer.refresh_from_db()
        self.assertTrue(self.viewer.check_password('newpassword123'))
