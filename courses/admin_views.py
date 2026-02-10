from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import timedelta
from django.contrib.auth.models import User

from .models import (
    Course, Instructor, Category, Enrollment, UserProfile, Section, Lesson,
    LessonProgress, Cart, CartItem, Order, OrderItem, Review, Discussion,
    DiscussionReply, Certificate, CourseMaterial
)
from .forms import CourseCreateForm, InstructorCreateForm, InstructorEditForm, CategoryForm

# Decorator to check if user is superuser
def superuser_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('courses:home')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

# ============================================================================
# CUSTOM ADMIN DASHBOARD
# ============================================================================

@login_required
@superuser_required
def admin_dashboard(request):
    """Main admin dashboard with overview statistics"""

    # Get date ranges
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)

    # Overall Statistics
    total_users = User.objects.count()
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()
    total_revenue = Order.objects.filter(status='completed').aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    # Recent Statistics
    new_users_30d = User.objects.filter(date_joined__date__gte=last_30_days).count()
    new_enrollments_30d = Enrollment.objects.filter(enrolled_at__date__gte=last_30_days).count()
    revenue_30d = Order.objects.filter(
        status='completed',
        created_at__date__gte=last_30_days
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Course Statistics
    published_courses = Course.objects.count()
    featured_courses = Course.objects.filter(is_featured=True).count()
    courses_by_level = Course.objects.values('level').annotate(count=Count('id'))

    # Enrollment Statistics
    completed_enrollments = Enrollment.objects.filter(completed=True).count()
    active_enrollments = Enrollment.objects.filter(completed=False).count()
    completion_rate = (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0

    # Revenue Statistics
    pending_orders = Order.objects.filter(status='pending').count()
    completed_orders = Order.objects.filter(status='completed').count()
    failed_orders = Order.objects.filter(status='failed').count()

    # Content Statistics
    total_lessons = Lesson.objects.count()
    total_sections = Section.objects.count()
    total_materials = CourseMaterial.objects.count()

    # Community Statistics
    total_reviews = Review.objects.count()
    avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0
    total_discussions = Discussion.objects.count()
    total_replies = DiscussionReply.objects.count()

    # Certificate Statistics
    total_certificates = Certificate.objects.count()
    certificates_30d = Certificate.objects.filter(issued_at__date__gte=last_30_days).count()

    # Recent Activity
    recent_enrollments = Enrollment.objects.select_related('student', 'course').order_by('-enrolled_at')[:5]
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    recent_reviews = Review.objects.select_related('student', 'course').order_by('-created_at')[:5]

    # Top Performing Courses
    top_courses = Course.objects.annotate(
        enrollment_count=Count('enrollments'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-enrollment_count')[:5]

    # Instructors Statistics
    total_instructors = Instructor.objects.count()
    instructors_stats = Instructor.objects.annotate(
        course_count=Count('courses'),
        student_count=Count('courses__enrollments', distinct=True)
    ).order_by('-student_count')[:5]

    context = {
        # Overall Stats
        'total_users': total_users,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'total_revenue': total_revenue,

        # Recent Stats
        'new_users_30d': new_users_30d,
        'new_enrollments_30d': new_enrollments_30d,
        'revenue_30d': revenue_30d,

        # Course Stats
        'published_courses': published_courses,
        'featured_courses': featured_courses,
        'courses_by_level': courses_by_level,

        # Enrollment Stats
        'completed_enrollments': completed_enrollments,
        'active_enrollments': active_enrollments,
        'completion_rate': round(completion_rate, 2),

        # Revenue Stats
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'failed_orders': failed_orders,

        # Content Stats
        'total_lessons': total_lessons,
        'total_sections': total_sections,
        'total_materials': total_materials,

        # Community Stats
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 2),
        'total_discussions': total_discussions,
        'total_replies': total_replies,

        # Certificate Stats
        'total_certificates': total_certificates,
        'certificates_30d': certificates_30d,

        # Recent Activity
        'recent_enrollments': recent_enrollments,
        'recent_orders': recent_orders,
        'recent_reviews': recent_reviews,

        # Top Performing
        'top_courses': top_courses,

        # Instructors
        'total_instructors': total_instructors,
        'instructors_stats': instructors_stats,
    }

    return render(request, 'custom_admin/dashboard.html', context)

# ============================================================================
# USER MANAGEMENT
# ============================================================================

@login_required
@superuser_required
def admin_users_list(request):
    """List all users with filtering and search"""

    users = User.objects.select_related('profile').annotate(
        enrollment_count=Count('enrollments'),
        order_count=Count('orders')
    ).order_by('-date_joined')

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    # Filter by user type
    user_type = request.GET.get('type', '')
    if user_type == 'staff':
        users = users.filter(is_staff=True)
    elif user_type == 'superuser':
        users = users.filter(is_superuser=True)
    elif user_type == 'active':
        users = users.filter(is_active=True)
    elif user_type == 'inactive':
        users = users.filter(is_active=False)

    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)

    context = {
        'users': users_page,
        'search_query': search_query,
        'user_type': user_type,
        'total_users': users.count(),
    }

    return render(request, 'custom_admin/users_list.html', context)

@login_required
@superuser_required
def admin_user_detail(request, user_id):
    """Detailed view of a specific user"""

    user = get_object_or_404(User.objects.select_related('profile'), id=user_id)

    # User's enrollments
    enrollments = Enrollment.objects.filter(student=user).select_related('course').order_by('-enrolled_at')

    # User's orders
    orders = Order.objects.filter(user=user).order_by('-created_at')

    # User's reviews
    reviews = Review.objects.filter(student=user).select_related('course').order_by('-created_at')

    # User's certificates
    certificates = Certificate.objects.filter(student=user).select_related('course').order_by('-issued_at')

    # User's discussions
    discussions = Discussion.objects.filter(author=user).order_by('-created_at')

    # Statistics
    total_spent = orders.filter(status='completed').aggregate(total=Sum('total_amount'))['total'] or 0
    completion_rate = enrollments.filter(completed=True).count() / enrollments.count() * 100 if enrollments.count() > 0 else 0

    context = {
        'user_obj': user,
        'enrollments': enrollments,
        'orders': orders,
        'reviews': reviews,
        'certificates': certificates,
        'discussions': discussions,
        'total_spent': total_spent,
        'completion_rate': round(completion_rate, 2),
    }

    return render(request, 'custom_admin/user_detail.html', context)

@login_required
@superuser_required
def admin_toggle_user_status(request, user_id):
    """Toggle user active status"""

    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.is_active = not user.is_active
        user.save()

        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.username} has been {status}.')

    return redirect('courses:admin_user_detail', user_id=user_id)

# ============================================================================
# COURSE MANAGEMENT
# ============================================================================

@login_required
@superuser_required
def admin_courses_list(request):
    """List all courses with filtering"""

    courses = Course.objects.select_related('instructor', 'category').annotate(
        enrollment_count=Count('enrollments'),
        avg_rating=Avg('reviews__rating'),
        revenue=Sum('orderitem__order__total_amount', filter=Q(orderitem__order__status='completed'))
    ).order_by('-created_at')

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Filter by category
    category_id = request.GET.get('category', '')
    if category_id:
        courses = courses.filter(category_id=category_id)

    # Filter by level
    level = request.GET.get('level', '')
    if level:
        courses = courses.filter(level=level)

    # Filter by featured
    featured = request.GET.get('featured', '')
    if featured == 'yes':
        courses = courses.filter(is_featured=True)
    elif featured == 'no':
        courses = courses.filter(is_featured=False)

    # Pagination
    paginator = Paginator(courses, 20)
    page_number = request.GET.get('page')
    courses_page = paginator.get_page(page_number)

    # Get all categories for filter
    categories = Category.objects.all()

    context = {
        'courses': courses_page,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_level': level,
        'selected_featured': featured,
        'total_courses': courses.count(),
    }

    return render(request, 'custom_admin/courses_list.html', context)

@login_required
@superuser_required
def admin_course_detail(request, course_id):
    """Detailed view of a specific course"""

    course = get_object_or_404(
        Course.objects.select_related('instructor', 'category').annotate(
            enrollment_count=Count('enrollments'),
            avg_rating=Avg('reviews__rating'),
            revenue=Sum('orderitem__order__total_amount', filter=Q(orderitem__order__status='completed'))
        ),
        id=course_id
    )

    # Course sections and lessons
    sections = Section.objects.filter(course=course).prefetch_related('lessons').order_by('order')

    # Course materials
    materials = CourseMaterial.objects.filter(lesson__section__course=course).select_related('lesson')

    # Enrollments
    enrollments = Enrollment.objects.filter(course=course).select_related('student').order_by('-enrolled_at')[:10]

    # Reviews
    reviews = Review.objects.filter(course=course).select_related('student').order_by('-created_at')[:10]

    # Discussions
    discussions = Discussion.objects.filter(course=course).select_related('author').order_by('-created_at')[:10]

    # Statistics
    total_students = enrollments.model.objects.filter(course=course).count()
    completed_students = enrollments.model.objects.filter(course=course, completed=True).count()
    completion_rate = completed_students / total_students * 100 if total_students > 0 else 0

    context = {
        'course': course,
        'sections': sections,
        'materials': materials,
        'enrollments': enrollments,
        'reviews': reviews,
        'discussions': discussions,
        'total_students': total_students,
        'completed_students': completed_students,
        'completion_rate': round(completion_rate, 2),
    }

    return render(request, 'custom_admin/course_detail.html', context)

@login_required
@superuser_required
def admin_toggle_course_featured(request, course_id):
    """Toggle course featured status"""

    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        course.is_featured = not course.is_featured
        course.save()

        status = 'featured' if course.is_featured else 'unfeatured'
        messages.success(request, f'Course "{course.title}" has been {status}.')

    return redirect('courses:admin_course_detail', course_id=course_id)

# ============================================================================
# ORDER & PAYMENT MANAGEMENT
# ============================================================================

@login_required
@superuser_required
def admin_orders_list(request):
    """List all orders with filtering"""

    orders = Order.objects.select_related('user').annotate(
        items_count=Count('items')
    ).order_by('-created_at')

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            Q(order_id__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(payment_reference__icontains=search_query)
        )

    # Filter by status
    status = request.GET.get('status', '')
    if status:
        orders = orders.filter(status=status)

    # Filter by date
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)

    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    orders_page = paginator.get_page(page_number)

    # Statistics
    total_revenue = orders.filter(status='completed').aggregate(total=Sum('total_amount'))['total'] or 0
    pending_revenue = orders.filter(status='pending').aggregate(total=Sum('total_amount'))['total'] or 0

    context = {
        'orders': orders_page,
        'search_query': search_query,
        'selected_status': status,
        'date_from': date_from,
        'date_to': date_to,
        'total_orders': orders.count(),
        'total_revenue': total_revenue,
        'pending_revenue': pending_revenue,
    }

    return render(request, 'custom_admin/orders_list.html', context)

@login_required
@superuser_required
def admin_order_detail(request, order_id):
    """Detailed view of a specific order"""

    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items__course'),
        order_id=order_id
    )

    context = {
        'order': order,
    }

    return render(request, 'custom_admin/order_detail.html', context)

@login_required
@superuser_required
def admin_update_order_status(request, order_id):
    """Update order status"""

    if request.method == 'POST':
        order = get_object_or_404(Order, order_id=order_id)
        new_status = request.POST.get('status')

        if new_status in dict(Order._meta.get_field('status').choices):
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {new_status}.')
        else:
            messages.error(request, 'Invalid status.')

    return redirect('courses:admin_order_detail', order_id=order_id)

# ============================================================================
# ENROLLMENT & PROGRESS TRACKING
# ============================================================================

@login_required
@superuser_required
def admin_enrollments_list(request):
    """List all enrollments with filtering"""

    enrollments = Enrollment.objects.select_related('student', 'course').order_by('-enrolled_at')

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        enrollments = enrollments.filter(
            Q(student__username__icontains=search_query) |
            Q(student__email__icontains=search_query) |
            Q(course__title__icontains=search_query)
        )

    # Filter by completion status
    completion_status = request.GET.get('completion', '')
    if completion_status == 'completed':
        enrollments = enrollments.filter(completed=True)
    elif completion_status == 'active':
        enrollments = enrollments.filter(completed=False)

    # Filter by course
    course_id = request.GET.get('course', '')
    if course_id:
        enrollments = enrollments.filter(course_id=course_id)

    # Pagination
    paginator = Paginator(enrollments, 20)
    page_number = request.GET.get('page')
    enrollments_page = paginator.get_page(page_number)

    # Get all courses for filter
    courses = Course.objects.all()

    context = {
        'enrollments': enrollments_page,
        'courses': courses,
        'search_query': search_query,
        'selected_completion': completion_status,
        'selected_course': course_id,
        'total_enrollments': enrollments.count(),
    }

    return render(request, 'custom_admin/enrollments_list.html', context)

@login_required
@superuser_required
def admin_enrollment_detail(request, enrollment_id):
    """Detailed view of a specific enrollment"""

    enrollment = get_object_or_404(
        Enrollment.objects.select_related('student', 'course'),
        id=enrollment_id
    )

    # Get lesson progress
    lesson_progress = LessonProgress.objects.filter(
        enrollment=enrollment
    ).select_related('lesson').order_by('lesson__section__order', 'lesson__order')

    context = {
        'enrollment': enrollment,
        'lesson_progress': lesson_progress,
    }

    return render(request, 'custom_admin/enrollment_detail.html', context)

# ============================================================================
# CERTIFICATE MANAGEMENT
# ============================================================================

@login_required
@superuser_required
def admin_certificates_list(request):
    """List all certificates"""

    certificates = Certificate.objects.select_related('student', 'course').order_by('-issued_at')

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        certificates = certificates.filter(
            Q(certificate_id__icontains=search_query) |
            Q(student__username__icontains=search_query) |
            Q(course__title__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(certificates, 20)
    page_number = request.GET.get('page')
    certificates_page = paginator.get_page(page_number)

    context = {
        'certificates': certificates_page,
        'search_query': search_query,
        'total_certificates': certificates.count(),
    }

    return render(request, 'custom_admin/certificates_list.html', context)

# ============================================================================
# REVIEWS & DISCUSSIONS MODERATION
# ============================================================================

@login_required
@superuser_required
def admin_reviews_list(request):
    """List all reviews with moderation options"""

    reviews = Review.objects.select_related('student', 'course').order_by('-created_at')

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        reviews = reviews.filter(
            Q(student__username__icontains=search_query) |
            Q(course__title__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(comment__icontains=search_query)
        )

    # Filter by rating
    rating = request.GET.get('rating', '')
    if rating:
        reviews = reviews.filter(rating=rating)

    # Pagination
    paginator = Paginator(reviews, 20)
    page_number = request.GET.get('page')
    reviews_page = paginator.get_page(page_number)

    context = {
        'reviews': reviews_page,
        'search_query': search_query,
        'selected_rating': rating,
        'total_reviews': reviews.count(),
    }

    return render(request, 'custom_admin/reviews_list.html', context)

@login_required
@superuser_required
def admin_delete_review(request, review_id):
    """Delete a review"""

    if request.method == 'POST':
        review = get_object_or_404(Review, id=review_id)
        course_title = review.course.title
        review.delete()
        messages.success(request, f'Review for "{course_title}" has been deleted.')

    return redirect('courses:admin_reviews_list')

@login_required
@superuser_required
def admin_discussions_list(request):
    """List all discussions with moderation options"""

    discussions = Discussion.objects.select_related('author', 'course').annotate(
        replies_count=Count('replies')
    ).order_by('-created_at')

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        discussions = discussions.filter(
            Q(author__username__icontains=search_query) |
            Q(course__title__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    # Filter by status
    status = request.GET.get('status', '')
    if status == 'pinned':
        discussions = discussions.filter(is_pinned=True)
    elif status == 'resolved':
        discussions = discussions.filter(is_resolved=True)
    elif status == 'unresolved':
        discussions = discussions.filter(is_resolved=False)

    # Pagination
    paginator = Paginator(discussions, 20)
    page_number = request.GET.get('page')
    discussions_page = paginator.get_page(page_number)

    context = {
        'discussions': discussions_page,
        'search_query': search_query,
        'selected_status': status,
        'total_discussions': discussions.count(),
    }

    return render(request, 'custom_admin/discussions_list.html', context)

@login_required
@superuser_required
def admin_toggle_discussion_pin(request, discussion_id):
    """Toggle discussion pin status"""

    if request.method == 'POST':
        discussion = get_object_or_404(Discussion, id=discussion_id)
        discussion.is_pinned = not discussion.is_pinned
        discussion.save()

        status = 'pinned' if discussion.is_pinned else 'unpinned'
        messages.success(request, f'Discussion has been {status}.')

    return redirect('courses:admin_discussions_list')

@login_required
@superuser_required
def admin_toggle_discussion_resolved(request, discussion_id):
    """Toggle discussion resolved status"""

    if request.method == 'POST':
        discussion = get_object_or_404(Discussion, id=discussion_id)
        discussion.is_resolved = not discussion.is_resolved
        discussion.save()

        status = 'marked as resolved' if discussion.is_resolved else 'marked as unresolved'
        messages.success(request, f'Discussion has been {status}.')

    return redirect('courses:admin_discussions_list')

@login_required
@superuser_required
def admin_delete_discussion(request, discussion_id):
    """Delete a discussion"""

    if request.method == 'POST':
        discussion = get_object_or_404(Discussion, id=discussion_id)
        course_title = discussion.course.title
        discussion.delete()
        messages.success(request, f'Discussion in "{course_title}" has been deleted.')

    return redirect('courses:admin_discussions_list')

# ============================================================================
# INSTRUCTORS MANAGEMENT
# ============================================================================

@login_required
@superuser_required
def admin_instructors_list(request):
    """List all instructors"""

    instructors = Instructor.objects.select_related('user').annotate(
        course_count=Count('courses'),
        student_count=Count('courses__enrollments', distinct=True),
        avg_rating=Avg('courses__reviews__rating')
    ).order_by('-student_count')

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        instructors = instructors.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(full_name__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(instructors, 20)
    page_number = request.GET.get('page')
    instructors_page = paginator.get_page(page_number)

    context = {
        'instructors': instructors_page,
        'search_query': search_query,
        'total_instructors': instructors.count(),
    }

    return render(request, 'custom_admin/instructors_list.html', context)

@login_required
@superuser_required
def admin_instructor_detail(request, instructor_id):
    """Detailed view of a specific instructor"""

    instructor = get_object_or_404(
        Instructor.objects.select_related('user').annotate(
            course_count=Count('courses'),
            student_count=Count('courses__enrollments', distinct=True),
            avg_rating=Avg('courses__reviews__rating')
        ),
        id=instructor_id
    )

    # Instructor's courses
    courses = Course.objects.filter(instructor=instructor).annotate(
        enrollment_count=Count('enrollments'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-created_at')

    context = {
        'instructor': instructor,
        'courses': courses,
    }

    return render(request, 'custom_admin/instructor_detail.html', context)

@login_required
@superuser_required
def admin_create_instructor(request):
    """Create new instructor"""
    if request.method == 'POST':
        form = InstructorCreateForm(request.POST, request.FILES)
        if form.is_valid():
            instructor = form.save()
            messages.success(request, f'Instructor "{instructor.full_name}" created successfully!')
            return redirect('courses:admin_instructor_detail', instructor_id=instructor.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = InstructorCreateForm()

    context = {
        'form': form,
    }
    return render(request, 'custom_admin/create_instructor.html', context)

@login_required
@superuser_required
def admin_edit_instructor(request, instructor_id):
    """Edit existing instructor"""
    instructor = get_object_or_404(Instructor, id=instructor_id)

    if request.method == 'POST':
        form = InstructorEditForm(request.POST, request.FILES, instance=instructor)
        if form.is_valid():
            instructor = form.save()
            messages.success(request, f'Instructor "{instructor.full_name}" updated successfully!')
            return redirect('courses:admin_instructor_detail', instructor_id=instructor.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = InstructorEditForm(instance=instructor)

    context = {
        'form': form,
        'instructor': instructor,
    }
    return render(request, 'custom_admin/edit_instructor.html', context)

@login_required
@superuser_required
def admin_delete_instructor(request, instructor_id):
    """Delete an instructor"""
    instructor = get_object_or_404(Instructor, id=instructor_id)

    if request.method == 'POST':
        instructor_name = instructor.full_name
        user = instructor.user

        # Delete the instructor (this will also cascade delete related objects)
        instructor.delete()

        # Optionally delete the associated user account
        if user and request.POST.get('delete_user') == 'yes':
            user.delete()
            messages.success(request, f'Instructor "{instructor_name}" and associated user account deleted successfully!')
        else:
            messages.success(request, f'Instructor "{instructor_name}" deleted successfully!')

        return redirect('courses:admin_instructors_list')

    # Count related objects to show in confirmation
    course_count = instructor.courses.count()

    context = {
        'instructor': instructor,
        'course_count': course_count,
    }
    return render(request, 'custom_admin/instructor_confirm_delete.html', context)

# ============================================================================
# CATEGORIES MANAGEMENT
# ============================================================================

@login_required
@superuser_required
def admin_categories_list(request):
    """List all categories"""

    categories = Category.objects.annotate(
        course_count=Count('course')
    ).order_by('name')

    context = {
        'categories': categories,
        'total_categories': categories.count(),
    }

    return render(request, 'custom_admin/categories_list.html', context)

@login_required
@superuser_required
def admin_create_category(request):
    """Create new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('courses:admin_categories_list')
    else:
        form = CategoryForm()

    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'custom_admin/category_form.html', context)

@login_required
@superuser_required
def admin_edit_category(request, category_id):
    """Edit existing category"""
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('courses:admin_categories_list')
    else:
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'category': category,
        'action': 'Edit',
    }
    return render(request, 'custom_admin/category_form.html', context)

@login_required
@superuser_required
def admin_delete_category(request, category_id):
    """Delete category"""
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        return redirect('courses:admin_categories_list')

    # If GET request, show confirmation
    context = {
        'category': category,
        'course_count': category.course_set.count(),
    }
    return render(request, 'custom_admin/category_confirm_delete.html', context)

# ============================================================================
# ALL-IN-ONE COURSE CREATOR
# ============================================================================

@login_required
@superuser_required
def admin_create_course(request):
    """All-in-one course creator - create course with sections, lessons, and materials"""
    import json

    if request.method == 'POST':
        form = CourseCreateForm(request.POST, request.FILES)

        if form.is_valid():
            # Create the course
            course = form.save()

            # Process sections and lessons from JSON data
            sections_data = json.loads(request.POST.get('sections_data', '[]'))

            for section_data in sections_data:
                # Create section
                section = Section.objects.create(
                    course=course,
                    title=section_data.get('title', ''),
                    description=section_data.get('description', ''),
                    order=section_data.get('order', 0)
                )

                # Create lessons for this section
                for lesson_data in section_data.get('lessons', []):
                    lesson = Lesson.objects.create(
                        section=section,
                        title=lesson_data.get('title', ''),
                        content_type=lesson_data.get('content_type', 'video'),
                        video_url=lesson_data.get('video_url', ''),
                        article_content=lesson_data.get('article_content', ''),
                        duration_minutes=lesson_data.get('duration_minutes', 0),
                        order=lesson_data.get('order', 0),
                        is_preview=lesson_data.get('is_preview', False)
                    )

            messages.success(request, f'Course "{course.title}" created successfully with all sections and lessons!')
            return redirect('courses:admin_course_detail', course_id=course.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseCreateForm()

    context = {
        'form': form,
    }

    return render(request, 'custom_admin/create_course.html', context)

@login_required
@superuser_required
def admin_edit_course(request, course_id):
    """Edit existing course with all sections and lessons"""
    import json

    course = get_object_or_404(Course, id=course_id)
    sections = Section.objects.filter(course=course).prefetch_related('lessons').order_by('order')

    if request.method == 'POST':
        # Prepare initial data for JSON fields
        initial_data = request.POST.copy()

        form = CourseCreateForm(request.POST, request.FILES, instance=course)

        if form.is_valid():
            # Update the course
            course = form.save()

            # Delete existing sections and lessons
            Section.objects.filter(course=course).delete()

            # Process sections and lessons from JSON data
            sections_data = json.loads(request.POST.get('sections_data', '[]'))

            for section_data in sections_data:
                # Create section
                section = Section.objects.create(
                    course=course,
                    title=section_data.get('title', ''),
                    description=section_data.get('description', ''),
                    order=section_data.get('order', 0)
                )

                # Create lessons for this section
                for lesson_data in section_data.get('lessons', []):
                    lesson = Lesson.objects.create(
                        section=section,
                        title=lesson_data.get('title', ''),
                        content_type=lesson_data.get('content_type', 'video'),
                        video_url=lesson_data.get('video_url', ''),
                        article_content=lesson_data.get('article_content', ''),
                        duration_minutes=lesson_data.get('duration_minutes', 0),
                        order=lesson_data.get('order', 0),
                        is_preview=lesson_data.get('is_preview', False)
                    )

            messages.success(request, f'Course "{course.title}" updated successfully!')
            return redirect('courses:admin_course_detail', course_id=course.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Prepare initial data for the form with text versions of JSON fields
        initial = {
            'what_you_will_learn': '\n'.join(course.what_you_will_learn) if course.what_you_will_learn else '',
            'requirements': '\n'.join(course.requirements) if course.requirements else '',
            'target_audience': '\n'.join(course.target_audience) if course.target_audience else '',
            'tags': ', '.join(course.tags) if course.tags else '',
        }
        form = CourseCreateForm(instance=course, initial=initial)

    # Prepare existing sections data as JSON for JavaScript
    existing_sections = []
    for section in sections:
        section_data = {
            'title': section.title,
            'description': section.description,
            'order': section.order,
            'lessons': []
        }
        for lesson in section.lessons.all():
            lesson_data = {
                'title': lesson.title,
                'content_type': lesson.content_type,
                'video_url': lesson.video_url,
                'article_content': lesson.article_content,
                'duration_minutes': lesson.duration_minutes,
                'order': lesson.order,
                'is_preview': lesson.is_preview
            }
            section_data['lessons'].append(lesson_data)
        existing_sections.append(section_data)

    context = {
        'form': form,
        'course': course,
        'existing_sections': json.dumps(existing_sections),
        'editing': True,
    }

    return render(request, 'custom_admin/create_course.html', context)


@login_required
@superuser_required
def admin_delete_course(request, course_id):
    """Delete a course"""
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        course_title = course.title

        # Delete the course (cascade delete will handle related objects)
        course.delete()

        messages.success(request, f'Course "{course_title}" and all related data deleted successfully!')
        return redirect('courses:admin_courses_list')

    # For GET requests, redirect to course detail (modal handles confirmation)
    return redirect('courses:admin_course_detail', course_id=course_id)
