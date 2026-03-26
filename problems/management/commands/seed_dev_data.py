import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class Command(BaseCommand):
    help = "Seed dev database with users and problems. Safe to rerun."

    def handle(self, *args, **options):
        # 1. Create dev users if we are in development
        # either DJANGO_ENV=development or settings.DEBUG
        django_env = os.environ.get("DJANGO_ENV", "").lower()
        is_dev = django_env == "development" or settings.DEBUG

        users_created = 0
        users_updated = 0

        if is_dev:
            # Create superuser
            admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
            admin_user, created = User.objects.get_or_create(
                username='admin',
                defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
            )
            if created:
                users_created += 1
                admin_user.set_password(admin_password)
                admin_user.save()
            else:
                users_updated += 1
                admin_user.set_password(admin_password)
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.save()

            # Create test users
            for i in range(1, 3):
                username = f'testuser{i}'
                test_user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'email': f'{username}@example.com'}
                )
                if created:
                    users_created += 1
                    test_user.set_unusable_password()
                    test_user.save()
                else:
                    users_updated += 1

            self.stdout.write(self.style.SUCCESS(f"Users seeded: {users_created} created, {users_updated} updated."))
        else:
            self.stdout.write(self.style.WARNING("Not in development mode (DEBUG=False and DJANGO_ENV!=development). Skipping dev users creation."))

        # 2. Call import_problems
        self.stdout.write("Running import_problems command...")
        call_command('import_problems')

        self.stdout.write(self.style.SUCCESS("seed_dev_data finished successfully."))
