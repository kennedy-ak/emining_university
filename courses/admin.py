from django.contrib import admin
from .models import (
    Category, Instructor, Course, Enrollment, UserProfile, Section, Lesson,
    CourseMaterial, LessonProgress, Cart, CartItem, Order, OrderItem,
    Review, Discussion, DiscussionReply, Certificate
)
from .forms import CategoryForm

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'country', 'city', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number']
    list_filter = ['country', 'created_at']
    date_hierarchy = 'created_at'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    list_display = ['name', 'slug', 'get_course_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'slug']
    ordering = ['name']

    def get_course_count(self, obj):
        """Display number of courses in this category"""
        return obj.course_set.count()
    get_course_count.short_description = 'Number of Courses'

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'profile_image']
    search_fields = ['full_name', 'user__username']
    list_filter = ['user']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'category', 'level', 'price', 'is_featured', 'created_at']
    list_filter = ['level', 'category', 'is_featured', 'created_at']
    search_fields = ['title', 'description', 'instructor__full_name']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_featured']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'progress_percentage', 'completed', 'enrolled_at']
    list_filter = ['completed', 'enrolled_at', 'course']
    search_fields = ['student__username', 'course__title']
    date_hierarchy = 'enrolled_at'
    readonly_fields = ['progress_percentage', 'completed_at']

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'created_at']
    list_filter = ['course', 'created_at']
    search_fields = ['title', 'course__title']
    ordering = ['course', 'order']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'section', 'content_type', 'duration_minutes', 'is_preview', 'order']
    list_filter = ['content_type', 'is_preview', 'section__course']
    search_fields = ['title', 'section__title']
    ordering = ['section', 'order']
    list_editable = ['is_preview']

@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['title', 'lesson__title']
    date_hierarchy = 'uploaded_at'

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'completed', 'completed_at', 'last_viewed']
    list_filter = ['completed', 'last_viewed']
    search_fields = ['student__username', 'lesson__title']
    date_hierarchy = 'last_viewed'
    readonly_fields = ['last_viewed']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'get_item_count']
    search_fields = ['user__username']
    date_hierarchy = 'created_at'

    def get_item_count(self, obj):
        return obj.get_item_count()
    get_item_count.short_description = 'Items'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'course', 'added_at']
    list_filter = ['added_at']
    search_fields = ['cart__user__username', 'course__title']
    date_hierarchy = 'added_at'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'total_amount', 'currency', 'status', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['order_id', 'user__username', 'payment_reference']
    date_hierarchy = 'created_at'
    readonly_fields = ['order_id', 'payment_reference', 'created_at', 'updated_at', 'completed_at']
    ordering = ['-created_at']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'course', 'price']
    list_filter = ['order__created_at']
    search_fields = ['order__order_id', 'course__title']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['course', 'student', 'rating', 'title', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['course__title', 'student__username', 'title', 'comment']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'author', 'is_pinned', 'is_resolved', 'created_at']
    list_filter = ['is_pinned', 'is_resolved', 'course', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    list_editable = ['is_pinned', 'is_resolved']
    date_hierarchy = 'created_at'
    ordering = ['-is_pinned', '-created_at']

@admin.register(DiscussionReply)
class DiscussionReplyAdmin(admin.ModelAdmin):
    list_display = ['discussion', 'author', 'is_instructor_reply', 'created_at']
    list_filter = ['is_instructor_reply', 'created_at']
    search_fields = ['discussion__title', 'author__username', 'content']
    date_hierarchy = 'created_at'
    ordering = ['discussion', 'created_at']

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_id', 'student', 'course', 'issued_at']
    list_filter = ['issued_at']
    search_fields = ['certificate_id', 'student__username', 'course__title']
    date_hierarchy = 'issued_at'
    readonly_fields = ['certificate_id', 'issued_at']
    ordering = ['-issued_at']
