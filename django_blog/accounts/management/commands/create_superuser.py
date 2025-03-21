from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Creates a default superuser for development'

    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        username = getattr(settings, 'DEV_ADMIN_USERNAME', 'admin@blog.com')
        password = getattr(settings, 'DEV_ADMIN_PASSWORD', 'admin')
        
        # Check if the user needs to be created
        if not User.objects.filter(email=username).exists():
            self.stdout.write(f'Creating superuser {username}')
            User.objects.create_superuser(username, password)
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
        else:
            self.stdout.write('Superuser already exists')