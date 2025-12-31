from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q, Avg, Count, Sum
from django.utils import timezone
from django.conf import settings
import json
import requests

from .models import (
    Course, Instructor, Category, Enrollment, UserProfile, Section, Lesson,
    LessonProgress, Cart, CartItem, Order, OrderItem, Review, Discussion,
    DiscussionReply, Certificate, CourseMaterial
)
from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm, ContactForm,
    ReviewForm, DiscussionForm, DiscussionReplyForm, CourseSearchForm
)
from .utils import (
    send_welcome_email, send_enrollment_email, send_certificate_email,
    send_contact_form_email, generate_certificate_pdf
)

# ============================================================================
# PUBLIC VIEWS
# ============================================================================

def home(request):
    """Homepage with featured courses"""
    featured_courses = Course.objects.filter(is_featured=True).select_related('instructor')[:6]
    total_courses = Course.objects.count()
    total_instructors = Instructor.objects.count()

    context = {
        'featured_courses': featured_courses,
        'total_courses': total_courses,
        'total_instructors': total_instructors,
    }
    return render(request, 'home.html', context)

def courses_list(request):
    """Course catalog with search and filtering"""
    courses = Course.objects.all().select_related('instructor', 'category').annotate(
        avg_rating=Avg('reviews__rating'),
        enrollment_count=Count('enrollments')
    )
    categories = Category.objects.all()

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(instructor__full_name__icontains=search_query)
        )

    # Filter by category
    category_filter = request.GET.get('category', '')
    if category_filter:
        courses = courses.filter(category__slug=category_filter)

    # Filter by level
    level_filter = request.GET.get('level', '')
    if level_filter:
        courses = courses.filter(level=level_filter)

    # Filter by price range
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    if price_min:
        try:
            courses = courses.filter(price__gte=float(price_min))
        except ValueError:
            pass
    if price_max:
        try:
            courses = courses.filter(price__lte=float(price_max))
        except ValueError:
            pass

    # Sort
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = ['price', '-price', '-created_at', 'title', '-enrollment_count', '-avg_rating']
    if sort_by in valid_sorts:
        courses = courses.order_by(sort_by)

    context = {
        'courses': courses,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'level_filter': level_filter,
        'sort_by': sort_by,
    }
    return render(request, 'courses/courses_list.html', context)

def course_detail(request, slug):
    """Course detail page with reviews"""
    course = get_object_or_404(Course, slug=slug)
    reviews = course.reviews.select_related('student').all()
    sections = Section.objects.filter(course=course).prefetch_related('lessons').order_by('order')

    # Check if user is enrolled
    is_enrolled = False
    user_review = None
    in_cart = False
    is_in_wishlist = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
        user_review = Review.objects.filter(student=request.user, course=course).first()
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            in_cart = CartItem.objects.filter(cart=cart, course=course).exists()

    context = {
        'course': course,
        'reviews': reviews,
        'sections': sections,
        'is_enrolled': is_enrolled,
        'user_review': user_review,
        'in_cart': in_cart,
        'is_in_wishlist': is_in_wishlist,
        'average_rating': course.get_average_rating(),
        'rating_count': course.get_rating_count(),
        'enrollment_count': course.get_enrollment_count(),
    }
    return render(request, 'courses/course_detail.html', context)

def about(request):
    """About page"""
    return render(request, 'about.html')

def contact(request):
    """Contact page with form"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            send_contact_form_email(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message']
            )
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('courses:contact')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})

def instructors_list(request):
    """Instructor listing page"""
    instructors = Instructor.objects.all().annotate(
        course_count=Count('courses')
    )
    context = {
        'instructors': instructors,
    }
    return render(request, 'instructors.html', context)

def instructor_detail(request, instructor_id):
    """Instructor profile page with their courses"""
    instructor = get_object_or_404(Instructor, id=instructor_id)

    # Get all courses by this instructor with ratings and enrollment counts
    courses = Course.objects.filter(instructor=instructor).annotate(
        avg_rating=Avg('reviews__rating'),
        enrollment_count=Count('enrollments')
    )

    # Calculate instructor stats
    total_students = Enrollment.objects.filter(course__instructor=instructor).values('student').distinct().count()
    course_count = courses.count()

    # Calculate average rating across all instructor's courses
    all_reviews = Review.objects.filter(course__instructor=instructor)
    avg_instructor_rating = all_reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    total_reviews = all_reviews.count()

    context = {
        'instructor': instructor,
        'courses': courses,
        'total_students': total_students,
        'course_count': course_count,
        'avg_rating': round(avg_instructor_rating, 1),
        'total_reviews': total_reviews,
    }
    return render(request, 'instructors/instructor_detail.html', context)

# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('courses:dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile automatically
            UserProfile.objects.create(user=user)
            login(request, user)
            # Send welcome email
            send_welcome_email(user)
            messages.success(request, 'Registration successful! Welcome to E-miningCampus.')
            return redirect('courses:dashboard')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('courses:dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'courses:dashboard')
                return redirect(next_url)
    else:
        form = UserLoginForm()

    return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('courses:home')

@login_required
def profile_view(request):
    """User profile management"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('courses:profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'profile.html', {'form': form, 'profile': profile})

# ============================================================================
# DASHBOARD & COURSE CONTENT
# ============================================================================

@login_required
def dashboard(request):
    """User dashboard with enrollments and stats"""
    # Get user's enrollments with progress
    enrollments = Enrollment.objects.filter(student=request.user).select_related(
        'course', 'course__instructor'
    ).order_by('-enrolled_at')

    # Recalculate progress for each enrollment
    for enrollment in enrollments:
        enrollment.calculate_progress()

    # Get certificates
    certificates = Certificate.objects.filter(student=request.user).select_related('course')

    # Get recent lesson progress
    recent_progress = LessonProgress.objects.filter(student=request.user).select_related(
        'lesson', 'lesson__section__course'
    ).order_by('-last_viewed')[:5]

    # Calculate total learning hours
    total_minutes = 0
    for enrollment in enrollments:
        minutes = LessonProgress.objects.filter(
            student=request.user,
            lesson__section__course=enrollment.course,
            completed=True
        ).aggregate(total=Sum('lesson__duration_minutes'))['total'] or 0
        total_minutes += minutes
    total_hours = total_minutes // 60

    # Get cart count
    cart = Cart.objects.filter(user=request.user).first()
    cart_count = cart.get_item_count() if cart else 0

    context = {
        'enrollments': enrollments,
        'certificates': certificates,
        'recent_progress': recent_progress,
        'total_hours': total_hours,
        'cart_count': cart_count,
        'completed_courses': enrollments.filter(completed=True).count(),
        'in_progress_courses': enrollments.filter(completed=False).count(),
    }
    return render(request, 'dashboard.html', context)

@login_required
def course_content(request, slug):
    """View course content - only for enrolled students"""
    course = get_object_or_404(Course, slug=slug)
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()

    if not enrollment:
        messages.error(request, 'You must be enrolled to access course content.')
        return redirect('courses:course_detail', slug=slug)

    sections = Section.objects.filter(course=course).prefetch_related('lessons')

    # Calculate progress
    enrollment.calculate_progress()

    context = {
        'course': course,
        'sections': sections,
        'enrollment': enrollment,
    }
    return render(request, 'courses/course_content.html', context)

@login_required
def lesson_view(request, course_slug, lesson_id):
    """View individual lesson"""
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, id=lesson_id)

    # Check if student is enrolled or lesson is preview
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    if not enrollment and not lesson.is_preview:
        messages.error(request, 'You must be enrolled to access this lesson.')
        return redirect('courses:course_detail', slug=course_slug)

    # Track progress
    progress = None
    if enrollment:
        progress, created = LessonProgress.objects.get_or_create(
            student=request.user,
            lesson=lesson
        )

    # Get all sections for navigation
    sections = Section.objects.filter(course=course).prefetch_related('lessons')

    # Get course materials
    materials = CourseMaterial.objects.filter(lesson=lesson)

    context = {
        'course': course,
        'lesson': lesson,
        'sections': sections,
        'enrollment': enrollment,
        'progress': progress,
        'materials': materials,
    }
    return render(request, 'courses/lesson_detail.html', context)

@login_required
@require_POST
def mark_lesson_complete(request, lesson_id):
    """Mark a lesson as completed"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment = Enrollment.objects.filter(
        student=request.user,
        course=lesson.section.course
    ).first()

    if enrollment:
        progress, created = LessonProgress.objects.get_or_create(
            student=request.user,
            lesson=lesson
        )
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()

        # Recalculate course progress
        enrollment.calculate_progress()

        messages.success(request, f'Lesson "{lesson.title}" marked as complete!')

        return redirect('courses:lesson_view',
                       course_slug=lesson.section.course.slug,
                       lesson_id=lesson.id)

    messages.error(request, 'You must be enrolled to mark lessons as complete.')
    return redirect('courses:home')

# ============================================================================
# SHOPPING CART & PAYMENT
# ============================================================================

@login_required
def cart_view(request):
    """View shopping cart"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('course', 'course__instructor')

    context = {
        'cart': cart,
        'items': items,
        'total': cart.get_total(),
    }
    return render(request, 'cart/cart.html', context)

@login_required
@require_POST
def add_to_cart(request, course_id):
    """Add course to cart"""
    course = get_object_or_404(Course, id=course_id)

    # Check if already enrolled
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.warning(request, 'You are already enrolled in this course.')
        return redirect('courses:course_detail', slug=course.slug)

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, course=course)

    if created:
        messages.success(request, f'{course.title} added to cart!')
    else:
        messages.info(request, f'{course.title} is already in your cart.')

    return redirect('courses:cart')

@login_required
@require_POST
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    course_title = cart_item.course.title
    cart_item.delete()
    messages.success(request, f'{course_title} removed from cart.')
    return redirect('courses:cart')

@login_required
def checkout(request):
    """Checkout page"""
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.select_related('course')

    if not items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('courses:courses_list')

    context = {
        'cart': cart,
        'items': items,
        'total': cart.get_total(),
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
    }
    return render(request, 'cart/checkout.html', context)

@login_required
@require_POST
def initiate_payment(request):
    """Initiate Paystack payment"""
    cart = get_object_or_404(Cart, user=request.user)

    if not cart.items.exists():
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    # Create order
    order = Order()
    order.user = request.user
    order.order_id = order.generate_order_id()
    order.total_amount = cart.get_total()
    order.currency = 'GHS'
    order.status = 'pending'
    order.save()

    # Add order items
    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            course=cart_item.course,
            price=cart_item.course.price
        )

    # Initialize Paystack payment
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "email": request.user.email,
        "amount": int(order.total_amount * 100),  # Paystack uses pesewas (GHS * 100)
        "reference": order.order_id,
        "callback_url": request.build_absolute_uri('/payment/verify/')
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        if result['status']:
            return JsonResponse({
                'authorization_url': result['data']['authorization_url'],
                'reference': order.order_id
            })
        else:
            order.status = 'failed'
            order.save()
            return JsonResponse({'error': 'Payment initialization failed'}, status=400)
    except Exception as e:
        order.status = 'failed'
        order.save()
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def paystack_webhook(request):
    """Handle Paystack webhook for payment verification"""
    if request.method == 'POST':
        payload = json.loads(request.body)

        if payload['event'] == 'charge.success':
            reference = payload['data']['reference']

            try:
                order = Order.objects.get(order_id=reference)
                order.status = 'completed'
                order.payment_reference = payload['data']['id']
                order.payment_method = payload['data']['channel']
                order.completed_at = timezone.now()
                order.save()

                # Enroll user in courses
                for order_item in order.items.all():
                    Enrollment.objects.get_or_create(
                        student=order.user,
                        course=order_item.course
                    )

                # Clear cart
                Cart.objects.filter(user=order.user).delete()

                # Send confirmation email
                send_enrollment_email(order.user, order)

            except Order.DoesNotExist:
                pass

        return JsonResponse({'status': 'success'})

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def payment_verify(request):
    """Verify payment and show result"""
    reference = request.GET.get('reference')

    if not reference:
        messages.error(request, 'Invalid payment reference.')
        return redirect('courses:cart')

    try:
        order = Order.objects.get(order_id=reference, user=request.user)

        # Verify with Paystack
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        response = requests.get(url, headers=headers)
        result = response.json()

        if result['status'] and result['data']['status'] == 'success':
            order.status = 'completed'
            order.payment_reference = result['data']['id']
            order.payment_method = result['data']['channel']
            order.completed_at = timezone.now()
            order.save()

            # Enroll in courses
            for order_item in order.items.all():
                Enrollment.objects.get_or_create(
                    student=order.user,
                    course=order_item.course
                )

            # Clear cart
            Cart.objects.filter(user=order.user).delete()

            # Send enrollment email
            send_enrollment_email(order.user, order)

            messages.success(request, 'Payment successful! You have been enrolled in your courses.')
            return redirect('courses:dashboard')
        else:
            order.status = 'failed'
            order.save()
            messages.error(request, 'Payment verification failed.')
            return redirect('courses:cart')

    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('courses:cart')
    except Exception as e:
        messages.error(request, f'Error verifying payment: {str(e)}')
        return redirect('courses:cart')

# ============================================================================
# REVIEWS
# ============================================================================

@login_required
def add_review(request, slug):
    """Add review for a course"""
    course = get_object_or_404(Course, slug=slug)

    # Check if user is enrolled
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    if not enrollment:
        messages.error(request, 'You must be enrolled to review this course.')
        return redirect('courses:course_detail', slug=slug)

    # Check if already reviewed
    if Review.objects.filter(student=request.user, course=course).exists():
        messages.warning(request, 'You have already reviewed this course.')
        return redirect('courses:course_detail', slug=slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.student = request.user
            review.course = course
            review.save()
            messages.success(request, 'Thank you for your review!')
            return redirect('courses:course_detail', slug=slug)
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'courses/add_review.html', context)

@login_required
def edit_review(request, review_id):
    """Edit existing review"""
    review = get_object_or_404(Review, id=review_id, student=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review updated successfully!')
            return redirect('courses:course_detail', slug=review.course.slug)
    else:
        form = ReviewForm(instance=review)

    context = {
        'form': form,
        'course': review.course,
        'editing': True,
    }
    return render(request, 'courses/add_review.html', context)

# ============================================================================
# DISCUSSIONS
# ============================================================================

@login_required
def course_discussions(request, slug):
    """View all discussions for a course"""
    course = get_object_or_404(Course, slug=slug)

    # Check if enrolled
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    if not enrollment:
        messages.error(request, 'You must be enrolled to access discussions.')
        return redirect('courses:course_detail', slug=slug)

    discussions = course.discussions.select_related('author').all()

    context = {
        'course': course,
        'discussions': discussions,
    }
    return render(request, 'courses/discussions.html', context)

@login_required
def discussion_detail(request, discussion_id):
    """View single discussion with replies"""
    discussion = get_object_or_404(Discussion, id=discussion_id)

    # Check if enrolled
    enrollment = Enrollment.objects.filter(student=request.user, course=discussion.course).first()
    if not enrollment:
        messages.error(request, 'You must be enrolled to access discussions.')
        return redirect('courses:course_detail', slug=discussion.course.slug)

    replies = discussion.replies.select_related('author').all()

    if request.method == 'POST':
        form = DiscussionReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.discussion = discussion
            reply.author = request.user
            # Check if user is instructor
            reply.is_instructor_reply = (discussion.course.instructor.user == request.user)
            reply.save()
            messages.success(request, 'Reply posted successfully!')
            return redirect('courses:discussion_detail', discussion_id=discussion.id)
    else:
        form = DiscussionReplyForm()

    context = {
        'discussion': discussion,
        'replies': replies,
        'form': form,
        'course': discussion.course,
    }
    return render(request, 'courses/discussion_detail.html', context)

@login_required
def create_discussion(request, slug):
    """Create new discussion"""
    course = get_object_or_404(Course, slug=slug)

    # Check if enrolled
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    if not enrollment:
        messages.error(request, 'You must be enrolled to create discussions.')
        return redirect('courses:course_detail', slug=slug)

    if request.method == 'POST':
        form = DiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.course = course
            discussion.author = request.user
            discussion.save()
            messages.success(request, 'Discussion created successfully!')
            return redirect('courses:discussion_detail', discussion_id=discussion.id)
    else:
        form = DiscussionForm()

    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'courses/create_discussion.html', context)

# ============================================================================
# CERTIFICATES
# ============================================================================

@login_required
def download_certificate(request, certificate_id):
    """Download certificate PDF"""
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id, student=request.user)

    # Generate PDF if not exists
    if not certificate.pdf_file:
        pdf_buffer = generate_certificate_pdf(certificate)
        filename = f"certificate_{certificate.certificate_id}.pdf"
        certificate.pdf_file.save(filename, File(pdf_buffer))

    # Return PDF
    response = FileResponse(certificate.pdf_file.open('rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{certificate.certificate_id}.pdf"'
    return response

@login_required
def my_certificates(request):
    """View all user certificates"""
    certificates = Certificate.objects.filter(student=request.user).select_related('course')

    context = {
        'certificates': certificates,
    }
    return render(request, 'certificates/my_certificates.html', context)

def verify_certificate(request, certificate_id):
    """Public certificate verification"""
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id)

    context = {
        'certificate': certificate,
        'verified': True,
    }
    return render(request, 'certificates/verify.html', context)
