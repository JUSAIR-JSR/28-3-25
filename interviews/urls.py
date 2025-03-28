from django.urls import path
from .views import interview_list, create_interview, update_interview, delete_interview, interview_detail, manage_reviews, update_review_question, delete_review_question, add_interview_review

urlpatterns = [
    path('list/', interview_list, name='interview_list'),
    path('create/', create_interview, name='create_interview'),
    path('update/<int:interview_id>/', update_interview, name='update_interview'),
    path('delete/<int:interview_id>/', delete_interview, name='delete_interview'),
    path('detail/<int:interview_id>/', interview_detail, name='interview_detail'),
    path('manage_reviews/<int:interview_id>/', manage_reviews, name='manage_reviews'),
    path('update_review_question/<int:question_id>/', update_review_question, name='update_review_question'),
    path('delete_review_question/<int:question_id>/', delete_review_question, name='delete_review_question'),
    path('add_interview_review/<int:interview_id>/', add_interview_review, name='add_interview_review'),
]
