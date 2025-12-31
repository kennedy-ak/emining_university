from django.urls import path
from . import views
from . import admin_views

app_name = 'courses'

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('courses/', views.courses_list, name='courses_list'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('instructors/', views.instructors_list, name='instructors'),
    path('instructor/<int:instructor_id>/', views.instructor_detail, name='instructor_detail'),

    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # Dashboard & Course Content
    path('dashboard/', views.dashboard, name='dashboard'),
    path('course/<slug:slug>/content/', views.course_content, name='course_content'),
    path('course/<slug:course_slug>/lesson/<int:lesson_id>/', views.lesson_view, name='lesson_view'),
    path('lesson/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),

    # Shopping Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:course_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Payment
    path('checkout/', views.checkout, name='checkout'),
    path('payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('payment/verify/', views.payment_verify, name='payment_verify'),
    path('payment/webhook/', views.paystack_webhook, name='paystack_webhook'),

    # Reviews
    path('course/<slug:slug>/review/', views.add_review, name='add_review'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),

    # Discussions
    path('course/<slug:slug>/discussions/', views.course_discussions, name='course_discussions'),
    path('discussion/<int:discussion_id>/', views.discussion_detail, name='discussion_detail'),
    path('course/<slug:slug>/discussion/new/', views.create_discussion, name='create_discussion'),

    # Certificates
    path('certificates/', views.my_certificates, name='my_certificates'),
    path('certificate/<str:certificate_id>/download/', views.download_certificate, name='download_certificate'),
    path('certificate/<str:certificate_id>/verify/', views.verify_certificate, name='verify_certificate'),

    # ========== CUSTOM ADMIN PANEL ==========
    # Dashboard
    path('custom-admin/', admin_views.admin_dashboard, name='admin_dashboard'),

    # Users Management
    path('custom-admin/users/', admin_views.admin_users_list, name='admin_users_list'),
    path('custom-admin/users/<int:user_id>/', admin_views.admin_user_detail, name='admin_user_detail'),
    path('custom-admin/users/<int:user_id>/toggle-status/', admin_views.admin_toggle_user_status, name='admin_toggle_user_status'),

    # Courses Management
    path('custom-admin/courses/', admin_views.admin_courses_list, name='admin_courses_list'),
    path('custom-admin/courses/create/', admin_views.admin_create_course, name='admin_create_course'),
    path('custom-admin/courses/<int:course_id>/', admin_views.admin_course_detail, name='admin_course_detail'),
    path('custom-admin/courses/<int:course_id>/edit/', admin_views.admin_edit_course, name='admin_edit_course'),
    path('custom-admin/courses/<int:course_id>/toggle-featured/', admin_views.admin_toggle_course_featured, name='admin_toggle_course_featured'),

    # Orders Management
    path('custom-admin/orders/', admin_views.admin_orders_list, name='admin_orders_list'),
    path('custom-admin/orders/<str:order_id>/', admin_views.admin_order_detail, name='admin_order_detail'),
    path('custom-admin/orders/<str:order_id>/update-status/', admin_views.admin_update_order_status, name='admin_update_order_status'),

    # Enrollments Management
    path('custom-admin/enrollments/', admin_views.admin_enrollments_list, name='admin_enrollments_list'),
    path('custom-admin/enrollments/<int:enrollment_id>/', admin_views.admin_enrollment_detail, name='admin_enrollment_detail'),

    # Certificates Management
    path('custom-admin/certificates/', admin_views.admin_certificates_list, name='admin_certificates_list'),

    # Reviews Management
    path('custom-admin/reviews/', admin_views.admin_reviews_list, name='admin_reviews_list'),
    path('custom-admin/reviews/<int:review_id>/delete/', admin_views.admin_delete_review, name='admin_delete_review'),

    # Discussions Management
    path('custom-admin/discussions/', admin_views.admin_discussions_list, name='admin_discussions_list'),
    path('custom-admin/discussions/<int:discussion_id>/toggle-pin/', admin_views.admin_toggle_discussion_pin, name='admin_toggle_discussion_pin'),
    path('custom-admin/discussions/<int:discussion_id>/toggle-resolved/', admin_views.admin_toggle_discussion_resolved, name='admin_toggle_discussion_resolved'),
    path('custom-admin/discussions/<int:discussion_id>/delete/', admin_views.admin_delete_discussion, name='admin_delete_discussion'),

    # Instructors Management
    path('custom-admin/instructors/', admin_views.admin_instructors_list, name='admin_instructors_list'),
    path('custom-admin/instructors/create/', admin_views.admin_create_instructor, name='admin_create_instructor'),
    path('custom-admin/instructors/<int:instructor_id>/', admin_views.admin_instructor_detail, name='admin_instructor_detail'),

    # Categories Management
    path('custom-admin/categories/', admin_views.admin_categories_list, name='admin_categories_list'),
]
