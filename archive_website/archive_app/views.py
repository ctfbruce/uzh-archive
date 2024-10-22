# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden, JsonResponse
from django.urls import reverse
from django_htmx.http import HttpResponseClientRedirect
from .forms import UserCreationForm, UploadDocumentForm, VerificationForm
from .models import Document, Subject, Tag, Verification_Code
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authentication import TokenAuthentication
from .utils import generate_verification_code
from django.utils import timezone
from django.contrib import messages

def is_verified(user):
    return user.is_verified

def is_moderator(user):
    return user.is_moderator

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Send verification email logic here
            
            verification_code = Verification_Code.objects.create(user=user, code = generate_verification_code())
            verification_code.save()
            
            login(request, user)
            return redirect('verify_email')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def verify_code(request):
    """
    need to add all the necessary feedbacks for if the request is not post, if the user is already verified, is there was no provided code, if the code was wrong, if the verification went well
    """
    if request.method == "POST":
        user = request.user
        if not user.is_verified:
            
            if request.POST.get("verification_code"):
                valid_code = user.verification_code.filter(code = request.POST.get("verification_code"),
                                                           expires_by__gt=timezone.now()).first()
            
                if valid_code:
                    user.is_verified = True
                    user.save()
                    valid_code.delete()
                    messages.success(request, "Your email has been verified successfully!")

                    return redirect("home")
                else:
                    messages.error(request, "Invalid or expired verification code.")
                    return render(request, "verify.html")
        else:
            messages.info(request, "Your email is already verified.")

            return redirect("home")              
    else:
        form = VerificationForm()
        return render(request, "verify.html", {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    error = None
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error = 'Invalid email or password.'
    return render(request, 'login.html', {'error': error})

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def home(request):
    if not request.user.is_verified:
        return redirect('verification_required')
    subjects = Subject.objects.all()
    tags = Tag.objects.all()
    return render(request, 'home.html', {'subjects': subjects, 'tags': tags})

@login_required
def verification_required(request):
    return redirect("verify_email")

@login_required
def profile(request):
    
    
    total_upvotes = request.user.uploaded_documents.aggregate(total_upvotes=Count('upvotes'))['total_upvotes']

    return render(request, 'profile.html', {
        'user': request.user,
        'total_upvotes': total_upvotes,
    })
    
@login_required
def delete_profile(request):
    if request.method == 'POST':
        # Get the currently logged-in user
        user = request.user

    
        # Log out the user before deleting the profile
        logout(request)

        # Delete the user's profile
        user.delete()

        # Redirect to home or login page after deletion
        return redirect('home')  # Or you can redirect to 'login'

    # If the request is not a POST (e.g., GET), deny access
    return HttpResponseForbidden("You can only delete your profile via a POST request.")
    
    
@login_required
def upload_document(request):
    if not request.user.is_verified:
        return redirect('verification_required')
    if request.method == 'POST':
        form = UploadDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            return render(request, 'upload_success.html')
    else:
        form = UploadDocumentForm()
    return render(request, 'upload_document.html', {'form': form})



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def api_upload_document(request):
    user = request.user

    # Check if the user is verified
    if not hasattr(user, 'is_verified') or not user.is_verified:
        return Response(
            {'detail': 'Verification required.'},
            status=status.HTTP_403_FORBIDDEN
        )


    
    
    
    if request.method == 'POST':
        
        form = UploadDocumentForm(request.POST, request.FILES)
        
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            return Response(
                {'detail': 'Upload successful.'},
            status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'detail': f'Form is invalid: {form.errors}.'},
            status=status.HTTP_400_BAD_REQUEST
            )
    else:
        return Response(
                {'detail': 'Request must be POST.'},
            status=status.HTTP_400_BAD_REQUEST
            )

@login_required
@user_passes_test(is_moderator)
def approve_documents(request):
    if not request.user.is_verified:
        return redirect('verification_required')
    pending_docs = Document.objects.pending_documents()
    return render(request, 'approve_documents.html', {'pending_docs': pending_docs})

@login_required
@user_passes_test(is_moderator)
def approve_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    document.verified_by = request.user
    document.save()
    return redirect('approve_documents')

@login_required
@user_passes_test(is_moderator)
def reject_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    document.delete()
    return redirect('approve_documents')

@login_required
def select_subject(request):
    if not request.user.is_verified:
        return redirect('verification_required')
    subjects = Subject.objects.all()
    return render(request, 'partials/select_subject.html', {'subjects': subjects})

@login_required
def select_document_type(request):
    if not request.user.is_verified:
        return redirect('verification_required')
    subject_id = request.GET.get('subject_id')
    subject = get_object_or_404(Subject, id=subject_id)
    doc_types = Document.objects.filter(subject=subject).values_list('type', flat=True).distinct()
    return render(request, 'partials/select_document_type.html', {'doc_types': doc_types, 'subject_id': subject_id})

@login_required
def select_year(request):
    if not request.user.is_verified:
        return redirect('verification_required')
    subject_id = request.GET.get('subject_id')
    doc_type = request.GET.get('doc_type')
    

    if doc_type == "past_exam":
        years = Document.objects.filter(
        subject_id=subject_id).filter(Q(type='past_exam') | Q(type='exam_solution')).values_list(
            'year', 
            flat=True
        ).distinct()
    
    else:
        years = Document.objects.filter(subject_id=subject_id, type=doc_type).values_list('year', flat=True).distinct()

    print("years are", years)
    
    return render(request, 'partials/select_year.html', {'years': years, 'subject_id': subject_id, 'doc_type': doc_type})

@login_required
def select_semester(request):
    if not request.user.is_verified:
        return redirect('verification_required')
    subject_id = request.GET.get('subject_id')
    doc_type = request.GET.get('doc_type')
    year = request.GET.get('year')
    
    
    if doc_type == "past_exam":
        semesters = Document.objects.filter(
            subject_id=subject_id, year=year
        ).filter(Q(type='past_exam') | Q(type='exam_solution')).values_list('semester', flat=True).distinct()
    else:
        semesters = Document.objects.filter(
            subject_id=subject_id, type=doc_type, year=year
        ).values_list('semester', flat=True).distinct()
        
    
    
    return render(request, 'partials/select_semester.html', {
        'semesters': semesters,
        'subject_id': subject_id,
        'doc_type': doc_type,
        'year': year
    })

@login_required
def display_documents(request):
    if not request.user.is_verified:
        return redirect('verification_required')
    subject_id = request.GET.get('subject_id')
    doc_type = request.GET.get('doc_type')
    
    print("doctype is", doc_type)
    year = request.GET.get('year')
    semester = request.GET.get('semester')

    if doc_type == 'past_exam':
        
        print(" i got hit ")
        documents = Document.objects.filter(
            subject_id=subject_id,
            year=year,
            semester=semester,
            verified_by__isnull=False
        ).filter(
            Q(type='past_exam') | Q(type='exam_solution')  # Include both past_exam and past_exam_solution
        )
    else:
        # Standard filtering for other document types
        documents = Document.objects.filter(
            subject_id=subject_id,
            type=doc_type,
            year=year,
            semester=semester,
            verified_by__isnull=False
        )
        
    context = {
        'documents': documents,
        'subject_id': subject_id,
        'doc_type': doc_type,
        'year': year,
        'semester': semester
    }

    return render(request, 'partials/display_documents.html', context)

@login_required
def upvote_document(request, doc_id):
    if not request.user.is_verified:
        return redirect('verification_required')
    if request.method == 'POST':
        document = get_object_or_404(Document, id=doc_id)
        document.upvotes.add(request.user)
        document.save()
        # Return the updated vote buttons
        return render(request, 'partials/vote_buttons.html', {'document': document})
    else:
        return HttpResponseForbidden("Invalid request method.")

@login_required
def downvote_document(request, doc_id):
    if not request.user.is_verified:
        return redirect('verification_required')
    if request.method == 'POST':
        document = get_object_or_404(Document, id=doc_id)
        document.upvotes.remove(request.user)
        document.save()
        # Return the updated vote buttons
        return render(request, 'partials/vote_buttons.html', {'document': document})
    else:
        return HttpResponseForbidden("Invalid request method.")