# urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('', views.home, name='home'),
    path('verification-required/', views.verification_required, name='verification_required'),
    path('profile/', views.profile, name='profile'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),
    path('upload/', views.upload_document, name='upload_document'),
    path('api/upload/', views.api_upload_document, name='api_upload_document'),
    path('approve-documents/', views.approve_documents, name='approve_documents'),
    path('approve-document/<int:doc_id>/', views.approve_document, name='approve_document'),
    path('reject-document/<int:doc_id>/', views.reject_document, name='reject_document'),
    path('select-subject/', views.select_subject, name='select_subject'),
    path('select-document-type/', views.select_document_type, name='select_document_type'),
    path('select-year/', views.select_year, name='select_year'),
    path('select-semester/', views.select_semester, name='select_semester'),
    path('display-documents/', views.display_documents, name='display_documents'),
    path('upvote-document/<int:doc_id>/', views.upvote_document, name='upvote_document'),
    path('downvote-document/<int:doc_id>/', views.downvote_document, name='downvote_document'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)