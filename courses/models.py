from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cloudinary.models import CloudinaryField

class UserProfile(models.Model):
    """Extended user profile for students"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = CloudinaryField('image', folder='profiles', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, default='Ghana')
    city = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    profile_image = CloudinaryField('image', folder='instructors', blank=True, null=True)

    def __str__(self):
        return self.full_name

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=500, unique=True)
    description = models.TextField(blank=True)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='courses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='intermediate')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='₵')
    image = CloudinaryField('image', folder='courses', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    what_you_will_learn = models.JSONField(default=list, blank=True, help_text="List of learning outcomes")
    requirements = models.JSONField(default=list, blank=True, help_text="List of course requirements")
    target_audience = models.JSONField(default=list, blank=True, help_text="List of target audience descriptions")
    tags = models.JSONField(default=list, blank=True, help_text="List of course tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

    def get_average_rating(self):
        """Calculate average rating"""
        from django.db.models import Avg
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0

    def get_rating_count(self):
        """Get total number of ratings"""
        return self.reviews.count()

    def get_enrollment_count(self):
        """Get number of enrolled students"""
        return self.enrollments.count()

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

    def calculate_progress(self):
        """Calculate course completion percentage"""
        from django.db.models import Count
        total_lessons = Lesson.objects.filter(section__course=self.course).count()
        if total_lessons == 0:
            return 0
        completed_lessons = LessonProgress.objects.filter(
            student=self.student,
            lesson__section__course=self.course,
            completed=True
        ).count()
        self.progress_percentage = int((completed_lessons / total_lessons) * 100)
        if self.progress_percentage == 100 and not self.completed:
            self.completed = True
            self.completed_at = timezone.now()
            self.save()
            # Issue certificate
            self.issue_certificate()
        else:
            self.save()
        return self.progress_percentage

    def issue_certificate(self):
        """Issue certificate on course completion"""
        if self.completed and not Certificate.objects.filter(student=self.student, course=self.course).exists():
            certificate = Certificate.objects.create(
                student=self.student,
                course=self.course,
                certificate_id=Certificate.generate_certificate_id_static()
            )
            return certificate
        return None

class Section(models.Model):
    """Course sections/modules"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    """Individual lessons within sections"""
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('article', 'Article'),
        ('quiz', 'Quiz'),
    ]

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='video')
    video_url = models.URLField(blank=True, help_text="YouTube video URL")
    article_content = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=0, help_text="Lesson duration in minutes")
    order = models.PositiveIntegerField(default=0)
    is_preview = models.BooleanField(default=False, help_text="Can be viewed without enrollment")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.section.course.title} - {self.title}"

    def get_youtube_embed_url(self):
        """Convert YouTube URL to embed format"""
        if 'youtube.com/watch?v=' in self.video_url:
            video_id = self.video_url.split('watch?v=')[1].split('&')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        elif 'youtu.be/' in self.video_url:
            video_id = self.video_url.split('youtu.be/')[1].split('?')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        return self.video_url

class CourseMaterial(models.Model):
    """Downloadable course materials"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='course_materials/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class LessonProgress(models.Model):
    """Track student progress through lessons"""
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_viewed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'lesson']
        verbose_name_plural = "Lesson Progress"

    def __str__(self):
        return f"{self.student.username} - {self.lesson.title}"

class Cart(models.Model):
    """Shopping cart for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s cart"

    def get_total(self):
        return sum(item.course.price for item in self.items.all())

    def get_item_count(self):
        return self.items.count()

class CartItem(models.Model):
    """Items in shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'course']

    def __str__(self):
        return f"{self.cart.user.username} - {self.course.title}"

class Order(models.Model):
    """Order/Payment tracking"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_id = models.CharField(max_length=100, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='GHS')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_reference = models.CharField(max_length=200, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.user.username}"

    def generate_order_id(self):
        """Generate unique order ID"""
        import uuid
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"ORD-{timestamp}-{unique_id}"

class OrderItem(models.Model):
    """Courses in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.order.order_id} - {self.course.title}"

class Review(models.Model):
    """Course reviews and ratings"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['course', 'student']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.rating} stars)"

class Discussion(models.Model):
    """Course discussion threads"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='discussions')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussions')
    title = models.CharField(max_length=300)
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title

    def get_reply_count(self):
        return self.replies.count()

class DiscussionReply(models.Model):
    """Replies to discussion threads"""
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_instructor_reply = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name_plural = "Discussion Replies"

    def __str__(self):
        return f"Reply by {self.author.username} on {self.discussion.title}"

class Certificate(models.Model):
    """Course completion certificates"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    certificate_id = models.CharField(max_length=100, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='certificates/', blank=True, null=True)

    class Meta:
        unique_together = ['student', 'course']

    def __str__(self):
        return f"Certificate: {self.student.username} - {self.course.title}"

    @staticmethod
    def generate_certificate_id_static():
        """Generate unique certificate ID"""
        import uuid
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m')
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"CERT-{timestamp}-{unique_id}"