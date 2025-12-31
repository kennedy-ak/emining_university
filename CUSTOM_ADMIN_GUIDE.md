# Custom Admin Panel Guide

## Overview

A comprehensive custom admin panel has been created for the E-miningCampus LMS system. This panel provides an intuitive, modern interface for managing all aspects of the platform.

## Access

### Requirements
- Must be logged in as a **superuser**
- URL: `http://your-domain.com/custom-admin/`

### Creating a Superuser
If you don't have a superuser account yet, create one using:
```bash
python manage.py createsuperuser
```

### Accessing the Admin Panel
1. Log in to the main site with your superuser credentials
2. Click on the **"Admin Panel"** link in the navigation bar (appears only for superusers)
3. Alternatively, navigate directly to `/custom-admin/`

## Features

### 1. Dashboard (`/custom-admin/`)
**Overview Statistics:**
- Total Users, Courses, Enrollments, Revenue
- Recent activity (last 30 days)
- Enrollment completion rates
- Order status breakdown
- Community statistics (reviews, discussions)
- Certificate issuance tracking

**Visualizations:**
- Course distribution by level
- Top performing courses
- Top instructors by student count
- Recent enrollments, orders, and reviews

### 2. Users Management (`/custom-admin/users/`)
**Features:**
- View all registered users
- Search by username, email, name
- Filter by user type (active, inactive, staff, superuser)
- View detailed user profiles
- Track user enrollments, orders, reviews, certificates
- Activate/deactivate user accounts

**User Details:**
- Personal information (profile, contact details)
- Enrollment history with progress tracking
- Order history and total spending
- Reviews submitted
- Certificates earned
- Completion rate statistics

### 3. Courses Management (`/custom-admin/courses/`)
**Features:**
- View all courses with key metrics
- Search by title or description
- Filter by category, level, and featured status
- View course details including content structure
- Toggle featured status
- Track student enrollments and progress
- Monitor course revenue

**Course Details:**
- Complete course information
- Sections and lessons breakdown
- Student enrollment list with progress
- Recent reviews and ratings
- Discussion threads
- Edit course via Django admin link

### 4. Instructors Management (`/custom-admin/instructors/`)
**Features:**
- View all instructors
- Search by name or email
- Track instructor performance
- View courses taught
- Monitor student count per instructor
- Average rating across courses

**Instructor Details:**
- Profile information
- List of courses taught
- Total students reached
- Performance metrics

### 5. Enrollments Management (`/custom-admin/enrollments/`)
**Features:**
- View all course enrollments
- Search by student or course name
- Filter by completion status
- Track progress percentages
- View enrollment dates and completion dates

**Enrollment Details:**
- Student and course information
- Overall progress percentage
- Lesson-by-lesson completion tracking
- Last viewed timestamps

### 6. Orders & Payments (`/custom-admin/orders/`)
**Features:**
- View all orders
- Search by order ID, username, or payment reference
- Filter by status (pending, processing, completed, failed, refunded)
- Filter by date range
- Track total revenue
- Update order status manually

**Order Details:**
- Customer information
- Order items (courses purchased)
- Payment details and references
- Order status management

### 7. Certificates Management (`/custom-admin/certificates/`)
**Features:**
- View all issued certificates
- Search by certificate ID, student, or course
- Download certificate PDFs
- Verify certificate authenticity
- Track issuance dates

### 8. Reviews Management (`/custom-admin/reviews/`)
**Features:**
- View all course reviews
- Search by student, course, or content
- Filter by rating (1-5 stars)
- Moderate inappropriate reviews
- Delete reviews if necessary

### 9. Discussions Management (`/custom-admin/discussions/`)
**Features:**
- View all course discussions
- Search by title, content, or author
- Filter by status (pinned, resolved, unresolved)
- Pin important discussions
- Mark discussions as resolved/unresolved
- Delete inappropriate discussions

### 10. Categories Management (`/custom-admin/categories/`)
**Features:**
- View all course categories
- See course count per category
- Edit categories via Django admin
- View courses in each category

## User Interface

### Design Features
- **Modern UI:** Clean, professional design with gradient accents
- **Responsive:** Works on desktop, tablet, and mobile devices
- **Sidebar Navigation:** Fixed sidebar with all management sections
- **Statistics Cards:** Visual cards with icons for key metrics
- **Search & Filters:** Powerful search and filtering on all list views
- **Pagination:** Easy navigation through large datasets
- **Action Buttons:** Quick access to common actions

### Color Coding
- **Primary (Blue):** General information, students, enrollments
- **Success (Green):** Completed items, revenue, positive stats
- **Warning (Yellow/Orange):** Pending items, featured courses
- **Danger (Red):** Failed orders, delete actions
- **Info (Cyan):** Certificates, discussions, additional info

## Security

### Access Control
- **Superuser Only:** All admin views require superuser privileges
- **Custom Decorator:** `@superuser_required` decorator on all views
- **Login Required:** Must be authenticated to access
- **Error Handling:** Non-superusers are redirected with error message

### Permissions
```python
@login_required
@superuser_required
def admin_view(request):
    # View logic
```

## Integration with Django Admin

The custom admin panel complements Django's built-in admin:
- **View Data:** Custom admin for viewing and monitoring
- **Edit Data:** Links to Django admin for detailed editing
- **Quick Actions:** Common actions (toggle featured, update status) in custom admin
- **Complex Editing:** Use Django admin for complex model editing

## URL Structure

All custom admin URLs are prefixed with `/custom-admin/`:

```
/custom-admin/                          - Dashboard
/custom-admin/users/                    - Users list
/custom-admin/users/<id>/               - User detail
/custom-admin/courses/                  - Courses list
/custom-admin/courses/<id>/             - Course detail
/custom-admin/instructors/              - Instructors list
/custom-admin/instructors/<id>/         - Instructor detail
/custom-admin/enrollments/              - Enrollments list
/custom-admin/enrollments/<id>/         - Enrollment detail
/custom-admin/orders/                   - Orders list
/custom-admin/orders/<id>/              - Order detail
/custom-admin/certificates/             - Certificates list
/custom-admin/reviews/                  - Reviews list
/custom-admin/discussions/              - Discussions list
/custom-admin/categories/               - Categories list
```

## Common Tasks

### Featuring a Course
1. Go to Courses Management
2. Click on the course
3. Click "Feature Course" or "Unfeature Course"

### Updating Order Status
1. Go to Orders Management
2. Click on the order
3. Select new status from dropdown
4. Click "Update Status"

### Moderating Discussions
1. Go to Discussions Management
2. Use action buttons to:
   - Pin/Unpin (thumbtack icon)
   - Resolve/Unresolve (check icon)
   - Delete (trash icon)

### Viewing User Activity
1. Go to Users Management
2. Click on user
3. View their enrollments, orders, reviews, and certificates

### Activating/Deactivating Users
1. Go to Users Management
2. Click on user
3. Click "Activate User" or "Deactivate User"

## Technical Details

### Files Created
- `courses/admin_views.py` - All admin view functions
- `templates/custom_admin/base.html` - Admin panel base template
- `templates/custom_admin/dashboard.html` - Dashboard template
- `templates/custom_admin/users_list.html` - Users list template
- `templates/custom_admin/user_detail.html` - User detail template
- `templates/custom_admin/courses_list.html` - Courses list template
- `templates/custom_admin/course_detail.html` - Course detail template
- `templates/custom_admin/orders_list.html` - Orders list template
- `templates/custom_admin/order_detail.html` - Order detail template
- `templates/custom_admin/enrollments_list.html` - Enrollments list template
- `templates/custom_admin/enrollment_detail.html` - Enrollment detail template
- `templates/custom_admin/certificates_list.html` - Certificates list template
- `templates/custom_admin/reviews_list.html` - Reviews list template
- `templates/custom_admin/discussions_list.html` - Discussions list template
- `templates/custom_admin/instructors_list.html` - Instructors list template
- `templates/custom_admin/instructor_detail.html` - Instructor detail template
- `templates/custom_admin/categories_list.html` - Categories list template

### Dependencies
- Bootstrap 5.3.0
- Font Awesome 6.4.0
- Chart.js (for potential future analytics)
- Django ORM for database queries

### Database Queries
All views use optimized queries with:
- `select_related()` for foreign keys
- `prefetch_related()` for reverse relationships
- `annotate()` for aggregations
- Pagination for large datasets

## Support

For issues or questions:
1. Check this guide first
2. Review the Django documentation
3. Check the implementation in `admin_views.py`

## Future Enhancements

Potential additions:
- Advanced analytics and charts
- Export data to CSV/Excel
- Bulk operations
- Email notifications from admin panel
- Custom report generation
- Activity logs and audit trails

---

**Version:** 1.0
**Last Updated:** 2025-12-27
