from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Interview, ReviewQuestion, InterviewReview
from jobs.models import JobApplication
from .forms import InterviewForm, ReviewQuestionForm, InterviewReviewForm

@login_required
def create_interview(request):
    organization = request.user.organization
    if request.method == 'POST':
        form = InterviewForm(request.POST, organization=organization)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.job_application.job.organization = organization
            interview.save()
            return redirect('interview_list')
    else:
        form = InterviewForm(organization=organization)
    return render(request, 'interviews/create_interview.html', {'form': form})

@login_required
def update_interview(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id, job_application__job__organization=request.user.organization)
    if request.method == 'POST':
        form = InterviewForm(request.POST, instance=interview, organization=request.user.organization)
        if form.is_valid():
            form.save()
            return redirect('interview_list')
    else:
        form = InterviewForm(instance=interview, organization=request.user.organization)
    return render(request, 'interviews/update_interview.html', {'form': form, 'interview': interview})

@login_required
def delete_interview(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id, job_application__job__organization=request.user.organization)
    if request.method == 'POST':
        interview.delete()
        return redirect('interview_list')
    return render(request, 'interviews/delete_interview.html', {'interview': interview})

from django.shortcuts import render, get_object_or_404
from interviews.models import Interview
from jobs.models import JobPosting
from organizations.models import Organization

def interview_list(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)  # Get organization
    job_posts = JobPosting.objects.filter(organization=organization)  # Get job posts of this organization
    interviews = Interview.objects.filter(job_application__job__in=job_posts)  # Filter interviews via job application

    context = {
        'organization': organization,
        'interviews': interviews,
    }
    return render(request, 'interviews/interview_list.html', context)





@login_required
def interview_detail(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id)
    reviews = InterviewReview.objects.filter(interview=interview)
    return render(request, 'interviews/interview_detail.html', {'interview': interview, 'reviews': reviews})

@login_required
def manage_reviews(request, interview_id):
    questions = ReviewQuestion.objects.filter(organization=request.user.organization)
    reviews = InterviewReview.objects.filter(interview__job_application__job__organization=request.user.organization)

    if request.method == 'POST':
        if 'add_question' in request.POST:
            question_form = ReviewQuestionForm(request.POST)
            if question_form.is_valid():
                new_question = question_form.save(commit=False)
                new_question.organization = request.user.organization
                new_question.save()
                return redirect('manage_reviews', interview_id=interview_id)
        elif 'add_review' in request.POST:
            for question in questions:
                rating = request.POST.get(f'rating_{question.id}')
                answer = request.POST.get(f'answer_{question.id}')
                interview_id = request.POST.get(f'interview_{question.id}')
                if interview_id:
                    InterviewReview.objects.update_or_create(
                        interview_id=interview_id, question=question,
                        defaults={'rating': rating, 'answer': answer}
                    )
            return redirect('manage_reviews', interview_id=interview_id)

    question_form = ReviewQuestionForm()
    return render(request, 'interviews/manage_reviews.html', {
        'questions': questions,
        'reviews': reviews,
        'question_form': question_form,
        'interview_id': interview_id
    })




@login_required
def add_interview_review(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id)
    questions = ReviewQuestion.objects.filter(organization=request.user.organization)
    existing_reviews = InterviewReview.objects.filter(interview=interview)
    ratings = {review.question.id: review.rating for review in existing_reviews}

    if request.method == 'POST':
        for question in questions:
            rating = request.POST.get(f'rating_{question.id}')
            answer = request.POST.get(f'answer_{question.id}')
            InterviewReview.objects.update_or_create(
                interview=interview, question=question,
                defaults={'rating': rating, 'answer': answer}
            )
        return redirect('interview_detail', interview_id=interview.id)

    return render(request, 'interviews/add_interview_review.html', {
        'interview': interview,
        'questions': questions,
        'ratings': ratings,
        'interview_id': interview_id  # Make sure to pass interview_id to template
    })



@login_required
def update_review_question(request, question_id):
    review_question = get_object_or_404(ReviewQuestion, id=question_id, organization=request.user.organization)
    if request.method == 'POST':
        form = ReviewQuestionForm(request.POST, instance=review_question)
        if form.is_valid():
            form.save()
            return redirect('manage_reviews')
    else:
        form = ReviewQuestionForm(instance=review_question)
    return render(request, 'interviews/update_review_question.html', {'form': form, 'review_question': review_question})

@login_required
def delete_review_question(request, question_id):
    review_question = get_object_or_404(ReviewQuestion, id=question_id, organization=request.user.organization)
    interview_id = request.GET.get('interview_id')  # Retrieve interview_id from GET parameters
    print(f"GET interview_id: {interview_id}")  # Debugging line
    if request.method == 'POST':
        interview_id = request.POST.get('interview_id')  # Retrieve interview_id from POST parameters
        print(f"POST interview_id: {interview_id}")  # Debugging line
        review_question.delete()
        return redirect('manage_reviews', interview_id=interview_id)
    return render(request, 'interviews/delete_review_question.html', {
        'review_question': review_question,
        'interview_id': interview_id  # Pass interview_id to the template
    })




from django.shortcuts import render
from .models import Interview  # Replace with your actual interview model

def view_my_interviews(request):
    # Get interviews for the logged-in user
    interviews = Interview.objects.filter(job_application__applicant=request.user)
    
    return render(request, 'interviews/my_interviews.html', {'interviews': interviews})
