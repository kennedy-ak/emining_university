from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from courses.models import Course, Instructor, Category, Enrollment


class Command(BaseCommand):
    help = 'Remove all load testing data from the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('⚠️  This will DELETE all load test data!'))
        self.stdout.write('   - Test users (loadtest_user_*)')
        self.stdout.write('   - Test courses (test-course-*, load-test-course-*)')
        self.stdout.write('   - Test instructors')
        self.stdout.write('   - Test categories')
        self.stdout.write('')

        # Count before deletion
        total_users = User.objects.count()
        total_courses = Course.objects.count()
        total_instructors = Instructor.objects.count()

        # 1. Delete test users
        deleted_users = User.objects.filter(username__startswith='loadtest_user_').delete()
        self.stdout.write(self.style.SUCCESS(f"✓ Deleted {deleted_users[0]} test users"))

        # 2. Delete test instructor user
        deleted_instructor_user = User.objects.filter(username='test_instructor').delete()
        if deleted_instructor_user[0] > 0:
            self.stdout.write(self.style.SUCCESS("✓ Deleted test instructor user"))

        # 3. Delete testadmin
        deleted_testadmin = User.objects.filter(username='testadmin').delete()
        if deleted_testadmin[0] > 0:
            self.stdout.write(self.style.SUCCESS("✓ Deleted testadmin user"))

        # 4. Delete test courses by slug patterns
        deleted_courses = Course.objects.filter(slug__startswith='load-test-course-').delete()
        if deleted_courses[0] > 0:
            self.stdout.write(self.style.SUCCESS(f"✓ Deleted {deleted_courses[0]} load test courses"))

        deleted_test_courses = Course.objects.filter(slug__startswith='test-course-').delete()
        if deleted_test_courses[0] > 0:
            self.stdout.write(self.style.SUCCESS(f"✓ Deleted {deleted_test_courses[0]} test courses"))

        # 5. Delete test categories
        deleted_categories = Category.objects.filter(
            slug__in=['mining-engineering', 'geology', 'safety']
        ).delete()
        if deleted_categories[0] > 0:
            self.stdout.write(self.style.SUCCESS(f"✓ Deleted {deleted_categories[0]} test categories"))

        # 6. Clean up orphaned instructors
        orphaned_instructors = Instructor.objects.filter(user__isnull=True)
        orphaned_count = orphaned_instructors.count()
        orphaned_instructors.delete()
        if orphaned_count > 0:
            self.stdout.write(self.style.SUCCESS(f"✓ Deleted {orphaned_count} orphaned instructors"))

        # 7. Clean up orphaned enrollments
        orphaned_enrollments = Enrollment.objects.filter(course__isnull=True).delete()
        if orphaned_enrollments[0] > 0:
            self.stdout.write(self.style.SUCCESS(f"✓ Deleted {orphaned_enrollments[0]} orphaned enrollments"))

        # Show summary
        self.stdout.write(self.style.SUCCESS("\n" + "="*50))
        self.stdout.write(self.style.SUCCESS("CLEANUP SUMMARY"))
        self.stdout.write(self.style.SUCCESS("="*50))
        self.stdout.write(f"Users:    {total_users} → {User.objects.count()} ({total_users - User.objects.count()} deleted)")
        self.stdout.write(f"Courses:  {total_courses} → {Course.objects.count()} ({total_courses - Course.objects.count()} deleted)")
        self.stdout.write(f"Instructors: {total_instructors} → {Instructor.objects.count()} ({total_instructors - Instructor.objects.count()} deleted)")
        self.stdout.write(self.style.SUCCESS("="*50))
        self.stdout.write(self.style.SUCCESS("✅ Load test data cleanup complete!"))
