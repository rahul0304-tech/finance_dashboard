import os
import django
from decimal import Decimal
from django.utils import timezone

def seed_data():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_dashboard.settings')
    django.setup()

    from api.models import User, FinancialRecord

    print("Clearing existing data...")
    User.objects.all().delete()
    FinancialRecord.all_objects.all().delete()

    print("Creating users...")
    admin = User.objects.create_superuser(username='admin', password='admin', email='admin@gmail.com', role='ADMIN')
    
    for i in range(1, 6):
        User.objects.create_user(username=f'analyst{i}', password=f'analyst{i}', email=f'analyst{i}@gmail.com', role='ANALYST')
        
    for i in range(1, 21):
        User.objects.create_user(username=f'viewer{i}', password=f'viewer{i}', email=f'viewer{i}@gmail.com', role='VIEWER')

    print("Creating financial records...")
    today = timezone.now().date()
    
    from datetime import timedelta
    import random

    categories_income = ['Salary', 'Dividends', 'Freelance', 'Bonus', 'Investments']
    categories_expense = ['Groceries', 'Rent', 'Utilities', 'Entertainment', 'Transport', 'Healthcare']

    for i in range(50):
        is_income = random.choice([True, False])
        transaction_type = 'INCOME' if is_income else 'EXPENSE'
        category = random.choice(categories_income) if is_income else random.choice(categories_expense)
        amount = Decimal(random.uniform(10.0, 2000.0)).quantize(Decimal('0.01'))
        date = today - timedelta(days=random.randint(0, 60))
        
        FinancialRecord.objects.create(
            amount=amount, 
            transaction_type=transaction_type, 
            category=category, 
            date=date, 
            notes=f'Sample {category} transaction.'
        )

    print("Database seeded successfully!")

if __name__ == '__main__':
    seed_data()
