"""
Django management command to import courses and instructors from JSON files
Usage: python manage.py import_courses --instructors instructors.json --courses courses.json
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils.text import slugify
from courses.models import Instructor, Course, Category
import json
import os


class Command(BaseCommand):
    help = 'Import instructors and courses from JSON files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--instructors',
            type=str,
            help='Path to instructors JSON file',
        )
        parser.add_argument(
            '--courses',
            type=str,
            help='Path to courses JSON file',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing',
        )

    def handle(self, *args, **options):
        if options['clear']:
            confirm = input('This will delete all existing courses and instructors. Are you sure? (yes/no): ')
            if confirm.lower() == 'yes':
                Course.objects.all().delete()
                Instructor.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('Cleared existing data'))
            else:
                self.stdout.write('Cancelled')
                return

        # Import instructors first
        if options['instructors']:
            self.import_instructors(options['instructors'])

        # Import courses
        if options['courses']:
            self.import_courses(options['courses'])

        self.stdout.write(self.style.SUCCESS('Import completed successfully!'))

    def import_instructors(self, file_path):
        """Import instructors from JSON file"""
        if not os.path.exists(file_path):
            raise CommandError(f'File {file_path} does not exist')

        with open(file_path, 'r', encoding='utf-8') as f:
            instructors_data = json.load(f)

        created_count = 0
        updated_count = 0

        for instructor_data in instructors_data:
            # Create or get user account for instructor
            username = slugify(instructor_data['full_name'].replace(' ', '_'))
            email = instructor_data.get('email', f'{username}@emining.edu')

            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': instructor_data.get('first_name', ''),
                    'last_name': instructor_data.get('last_name', ''),
                }
            )

            # Create or update instructor
            instructor, created = Instructor.objects.update_or_create(
                user=user,
                defaults={
                    'full_name': instructor_data['full_name'],
                    'bio': instructor_data.get('bio', ''),
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created instructor: {instructor.full_name}'))
            else:
                updated_count += 1
                self.stdout.write(f'Updated instructor: {instructor.full_name}')

        self.stdout.write(self.style.SUCCESS(
            f'Instructors import complete: {created_count} created, {updated_count} updated'
        ))

    def import_courses(self, file_path):
        """Import courses from JSON file"""
        if not os.path.exists(file_path):
            raise CommandError(f'File {file_path} does not exist')

        with open(file_path, 'r', encoding='utf-8') as f:
            courses_data = json.load(f)

        created_count = 0
        updated_count = 0
        errors = []

        for course_data in courses_data:
            try:
                # Get or create category
                category = None
                if 'category' in course_data and course_data['category']:
                    category, _ = Category.objects.get_or_create(
                        name=course_data['category'],
                        defaults={'slug': slugify(course_data['category'])}
                    )

                # Get instructor
                instructor = None
                if 'instructor' in course_data:
                    try:
                        instructor = Instructor.objects.get(
                            full_name__iexact=course_data['instructor']
                        )
                    except Instructor.DoesNotExist:
                        # Create a default user and instructor if not found
                        username = slugify(course_data['instructor'].replace(' ', '_'))
                        user, _ = User.objects.get_or_create(
                            username=username,
                            defaults={
                                'email': f'{username}@emining.edu',
                            }
                        )
                        instructor, _ = Instructor.objects.get_or_create(
                            user=user,
                            defaults={'full_name': course_data['instructor']}
                        )

                # Create or update course
                course, created = Course.objects.update_or_create(
                    slug=slugify(course_data['title']),
                    defaults={
                        'title': course_data['title'],
                        'description': course_data.get('description', ''),
                        'instructor': instructor,
                        'category': category,
                        'level': course_data.get('level', 'intermediate'),
                        'price': course_data.get('price', 0),
                        'currency': course_data.get('currency', '₵'),
                        'is_featured': course_data.get('is_featured', False),
                    }
                )

                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Created course: {course.title}'))
                else:
                    updated_count += 1
                    self.stdout.write(f'Updated course: {course.title}')

            except Exception as e:
                error_msg = f"Error importing course '{course_data.get('title', 'Unknown')}': {str(e)}"
                errors.append(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))

        self.stdout.write(self.style.SUCCESS(
            f'Courses import complete: {created_count} created, {updated_count} updated'
        ))

        if errors:
            self.stdout.write(self.style.WARNING(f'{len(errors)} errors occurred'))
