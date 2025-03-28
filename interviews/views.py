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

@login_required
def interview_list(request):
    if request.user.is_staff:
        organization = request.user.organization
        interviews = Interview.objects.filter(job_application__job__organization=organization)
    else:
        interviews = Interview.objects.filter(job_application__applicant=request.user)
    
    interviews_with_reviews = []
    for interview in interviews:
        interview_with_reviews = {
            'interview': interview,
            'reviews': InterviewReview.objects.filter(interview=interview)
        }
        interviews_with_reviews.append(interview_with_reviews)
    
    return render(request, 'interviews/interview_list.html', {'interviews_with_reviews': interviews_with_reviews})



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

