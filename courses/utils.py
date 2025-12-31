from io import BytesIO
from django.core.files import File
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch

def generate_certificate_pdf(certificate):
    """Generate PDF certificate using ReportLab"""
    buffer = BytesIO()

    # Create canvas in landscape mode
    c = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    # Set colors
    c.setFillColorRGB(0.2, 0.4, 0.8)  # Blue

    # Border
    c.setLineWidth(3)
    c.setStrokeColorRGB(0.2, 0.4, 0.8)
    c.rect(0.5*inch, 0.5*inch, width-inch, height-inch, stroke=1, fill=0)

    # Inner border
    c.setLineWidth(1)
    c.rect(0.6*inch, 0.6*inch, width-1.2*inch, height-1.2*inch, stroke=1, fill=0)

    # Title
    c.setFont("Helvetica-Bold", 36)
    c.setFillColorRGB(0.2, 0.4, 0.8)
    c.drawCentredString(width/2, height-1.5*inch, "CERTIFICATE OF COMPLETION")

    # Subtitle
    c.setFont("Helvetica", 16)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(width/2, height-2*inch, "This is to certify that")

    # Student name
    c.setFont("Helvetica-Bold", 28)
    c.setFillColorRGB(0.2, 0.4, 0.8)
    student_name = f"{certificate.student.get_full_name() or certificate.student.username}"
    c.drawCentredString(width/2, height-2.7*inch, student_name)

    # Course completion text
    c.setFont("Helvetica", 16)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(width/2, height-3.3*inch, "has successfully completed the course")

    # Course title
    c.setFont("Helvetica-Bold", 22)
    c.setFillColorRGB(0.2, 0.4, 0.8)
    # Wrap long course titles
    course_title = certificate.course.title
    if len(course_title) > 50:
        words = course_title.split()
        line1 = ' '.join(words[:len(words)//2])
        line2 = ' '.join(words[len(words)//2:])
        c.drawCentredString(width/2, height-4*inch, line1)
        c.drawCentredString(width/2, height-4.4*inch, line2)
    else:
        c.drawCentredString(width/2, height-4*inch, course_title)

    # Date
    c.setFont("Helvetica", 14)
    c.setFillColorRGB(0, 0, 0)
    issue_date = certificate.issued_at.strftime("%B %d, %Y")
    c.drawCentredString(width/2, height-5.2*inch, f"Issued on: {issue_date}")

    # Certificate ID
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawCentredString(width/2, height-5.7*inch, f"Certificate ID: {certificate.certificate_id}")

    # Instructor signature section
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0, 0, 0)
    c.setLineWidth(1)
    c.line(width/2 - 2*inch, height-6.5*inch, width/2 + 2*inch, height-6.5*inch)
    c.drawCentredString(width/2, height-6.8*inch, certificate.course.instructor.full_name)
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawCentredString(width/2, height-7*inch, "Course Instructor")

    # Footer
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawCentredString(width/2, 0.7*inch, "E-miningCampus - Your Premier Mining Engineering Learning Platform")
    c.drawCentredString(width/2, 0.5*inch, "www.eminingcampus.com")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer

def send_welcome_email(user):
    """Send welcome email to new users"""
    try:
        subject = 'Welcome to E-miningCampus!'
        context = {'user': user, 'site_url': settings.SITE_URL}
        html_message = render_to_string('emails/welcome_email.html', context)
        plain_message = f"""
        Welcome to E-miningCampus, {user.get_full_name() or user.username}!

        Thank you for joining our learning platform. We're excited to have you here!

        Get started by exploring our courses: {settings.SITE_URL}/courses/

        Best regards,
        The E-miningCampus Team
        """

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=True,
        )
    except Exception as e:
        print(f"Error sending welcome email: {e}")

def send_enrollment_email(user, order):
    """Send enrollment confirmation email"""
    try:
        courses = [item.course for item in order.items.all()]
        subject = 'Course Enrollment Confirmation - E-miningCampus'
        context = {
            'user': user,
            'order': order,
            'courses': courses,
            'site_url': settings.SITE_URL
        }
        html_message = render_to_string('emails/enrollment_email.html', context)
        plain_message = f"""
        Hello {user.get_full_name() or user.username},

        Thank you for enrolling in courses on E-miningCampus!

        Order ID: {order.order_id}

        Enrolled Courses:
        {chr(10).join([f"- {course.title}" for course in courses])}

        Access your courses: {settings.SITE_URL}/dashboard/

        Best regards,
        The E-miningCampus Team
        """

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=True,
        )
    except Exception as e:
        print(f"Error sending enrollment email: {e}")

def send_certificate_email(user, certificate):
    """Send certificate notification email"""
    try:
        subject = f'Congratulations! You earned a certificate - {certificate.course.title}'
        context = {
            'user': user,
            'certificate': certificate,
            'download_url': f"{settings.SITE_URL}/certificate/{certificate.certificate_id}/download/",
            'verify_url': f"{settings.SITE_URL}/certificate/{certificate.certificate_id}/verify/",
            'site_url': settings.SITE_URL
        }
        html_message = render_to_string('emails/certificate_email.html', context)
        plain_message = f"""
        Congratulations {user.get_full_name() or user.username}!

        You've successfully completed {certificate.course.title}!

        Certificate ID: {certificate.certificate_id}

        Download your certificate: {settings.SITE_URL}/certificate/{certificate.certificate_id}/download/
        Verify your certificate: {settings.SITE_URL}/certificate/{certificate.certificate_id}/verify/

        Best regards,
        The E-miningCampus Team
        """

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=True,
        )
    except Exception as e:
        print(f"Error sending certificate email: {e}")

def send_contact_form_email(name, email, subject, message):
    """Send contact form submission"""
    try:
        email_subject = f"Contact Form Submission: {subject}"
        email_message = f"""
        Contact Form Submission

        From: {name}
        Email: {email}
        Subject: {subject}

        Message:
        {message}

        ---
        This message was sent via the E-miningCampus contact form.
        """

        send_mail(
            email_subject,
            email_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.CONTACT_EMAIL],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Error sending contact form email: {e}")
