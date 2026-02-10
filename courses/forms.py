from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import (
    UserProfile, Review, Discussion, DiscussionReply, Category, Course,
    Section, Lesson, CourseMaterial, Instructor
)

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, max_length=150)
    last_name = forms.CharField(required=True, max_length=150)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Sign Up', css_class='btn btn-primary btn-lg w-100'))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email address already in use.')
        return email

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Login', css_class='btn btn-primary btn-lg w-100'))

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'bio', 'profile_picture', 'date_of_birth', 'country', 'city']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Update Profile', css_class='btn btn-primary'))

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your Name'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your Email'
    }))
    subject = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Subject'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 6,
        'class': 'form-control',
        'placeholder': 'Your Message'
    }), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Send Message', css_class='btn btn-primary'))

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, '⭐' * i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Share your experience with this course...'}),
            'title': forms.TextInput(attrs={'placeholder': 'Summary of your review'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit Review', css_class='btn btn-primary'))

class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Discussion topic...'}),
            'content': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Start the discussion...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Create Discussion', css_class='btn btn-primary'))

class DiscussionReplyForm(forms.ModelForm):
    class Meta:
        model = DiscussionReply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your reply...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Post Reply', css_class='btn btn-primary'))

class CourseSearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Search courses...',
        'class': 'form-control'
    }))
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    level = forms.ChoiceField(
        choices=[('', 'All Levels')] + Course.LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sort = forms.ChoiceField(
        choices=[
            ('-created_at', 'Newest First'),
            ('price', 'Price: Low to High'),
            ('-price', 'Price: High to Low'),
            ('title', 'Title: A-Z'),
        ],
        required=False,
        initial='-created_at',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

# ============================================================================
# CATEGORY FORM
# ============================================================================

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Category name (e.g., Mining Engineering)',
                'autofocus': True
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'category-slug (auto-generated from name)',
            }),
        }
        help_texts = {
            'name': 'Enter the category name',
            'slug': 'URL-friendly version of the name (will auto-populate)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make slug field optional for initial creation (will auto-populate)
        self.fields['slug'].required = False

    def clean_slug(self):
        from django.utils.text import slugify
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name', '')

        # Auto-generate slug from name if not provided
        if not slug and name:
            slug = slugify(name)

        return slug

# ============================================================================
# ALL-IN-ONE COURSE CREATOR FORMS
# ============================================================================

class CourseCreateForm(forms.ModelForm):
    # JSON fields as text areas for easier editing
    what_you_will_learn = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Enter learning outcomes (one per line)',
            'class': 'form-control'
        }),
        help_text='Enter each learning outcome on a new line'
    )
    requirements = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Enter requirements (one per line)',
            'class': 'form-control'
        }),
        help_text='Enter each requirement on a new line'
    )
    target_audience = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Enter target audience (one per line)',
            'class': 'form-control'
        }),
        help_text='Enter each audience description on a new line'
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter tags separated by commas',
            'class': 'form-control'
        }),
        help_text='Enter tags separated by commas (e.g., Mining, Geology, Exploration)'
    )

    class Meta:
        model = Course
        fields = [
            'title', 'slug', 'description', 'instructor', 'category',
            'level', 'price', 'currency', 'image', 'is_featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course title'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'course-url-slug'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Course description'}),
            'instructor': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_what_you_will_learn(self):
        data = self.cleaned_data.get('what_you_will_learn', '')
        if data:
            return [line.strip() for line in data.split('\n') if line.strip()]
        return []

    def clean_requirements(self):
        data = self.cleaned_data.get('requirements', '')
        if data:
            return [line.strip() for line in data.split('\n') if line.strip()]
        return []

    def clean_target_audience(self):
        data = self.cleaned_data.get('target_audience', '')
        if data:
            return [line.strip() for line in data.split('\n') if line.strip()]
        return []

    def clean_tags(self):
        data = self.cleaned_data.get('tags', '')
        if data:
            return [tag.strip() for tag in data.split(',') if tag.strip()]
        return []

    def save(self, commit=True):
        course = super().save(commit=False)

        # Manually set the JSONField data from cleaned data
        course.what_you_will_learn = self.cleaned_data.get('what_you_will_learn', [])
        course.requirements = self.cleaned_data.get('requirements', [])
        course.target_audience = self.cleaned_data.get('target_audience', [])
        course.tags = self.cleaned_data.get('tags', [])

        if commit:
            course.save()

        return course

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['title', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Section title (e.g., Week 1: Introduction)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Section description (optional)'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content_type', 'video_url', 'article_content', 'duration_minutes', 'order', 'is_preview']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lesson title'}),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'YouTube video URL'}),
            'article_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Article content'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Duration in minutes'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'is_preview': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Material title'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

# ============================================================================
# INSTRUCTOR CREATION FORM
# ============================================================================

class InstructorCreateForm(forms.ModelForm):
    # User fields
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username for login'
        }),
        help_text='Username for the instructor to login'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'instructor@example.com'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        }),
        help_text='Password for the instructor account'
    )
    password_confirm = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        }),
        label='Confirm Password'
    )

    class Meta:
        model = Instructor
        fields = ['full_name', 'bio', 'profile_image']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name of the instructor'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Brief biography of the instructor'
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Passwords do not match.')

        return cleaned_data

    def save(self, commit=True):
        # Create the user first
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            is_staff=True  # Give instructor staff access
        )

        # Create the instructor
        instructor = super().save(commit=False)
        instructor.user = user

        if commit:
            instructor.save()

        return instructor

class InstructorEditForm(forms.ModelForm):
    """Form for editing existing instructors"""

    # User email field (username cannot be changed)
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'instructor@example.com'
        })
    )

    class Meta:
        model = Instructor
        fields = ['full_name', 'bio', 'profile_image']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name of the instructor'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Brief biography of the instructor'
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email already exists for another user
        if User.objects.filter(email=email).exclude(id=self.instance.user.id).exists():
            raise forms.ValidationError('Email already exists for another user.')
        return email

    def save(self, commit=True):
        instructor = super().save(commit=False)

        # Update user email
        if self.instance.user:
            self.instance.user.email = self.cleaned_data['email']
            if commit:
                self.instance.user.save()

        if commit:
            instructor.save()

        return instructor
