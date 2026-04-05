import os

def build_schema():
    print("Building database schema...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_dashboard.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django."
        ) from exc
    execute_from_command_line(['manage.py', 'makemigrations', 'api'])
    execute_from_command_line(['manage.py', 'migrate'])
    print("Schema built successfully!")

if __name__ == '__main__':
    build_schema()
