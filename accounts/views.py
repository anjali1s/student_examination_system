
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile, Course, Subject, Exam, Question, StudentExam, Result
from django.utils import timezone

# ===== Login =====
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            return render(request, 'accounts/login.html', {'error': 'Invalid username'})

        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(request, 'accounts/login.html', {'error': 'Invalid password'})

        auth_login(request, user)
        if hasattr(user, 'profile') and user.profile.role == 'teacher':
            return redirect('teacher_dashboard')
        return redirect('student_dashboard')

    return render(request, 'accounts/login.html')


# ===== Logout =====
def logout_view(request):
    auth_logout(request)
    return redirect('login')


# ===== Teacher dashboard (ENHANCED) =====
@login_required
def teacher_dashboard(request):
    # Get all exams created by this teacher
    exams = Exam.objects.filter(created_by=request.user).order_by('-start_time')
    
    # Calculate statistics
    total_students = Profile.objects.filter(role='student', approved=True).count()
    
    completed_exams = StudentExam.objects.filter(
        exam__created_by=request.user, 
        is_submitted=True
    ).count()
    
    all_scores = StudentExam.objects.filter(
        exam__created_by=request.user, 
        is_submitted=True, 
        score__isnull=False
    )
    
    if all_scores.exists():
        scores = [s.score for s in all_scores if s.score is not None]
        average_score = round(sum(scores) / len(scores), 1) if scores else 0
    else:
        average_score = 0
    
    context = {
        'exams': exams,
        'total_students': total_students,
        'completed_exams': completed_exams,
        'average_score': average_score,
    }
    
    return render(request, 'accounts/teacher_dashboard.html', context)


# ===== Create Exam =====
@login_required
def teacher_create_exam(request):
    courses = Course.objects.all()
    subjects = Subject.objects.all()
    if request.method == 'POST':
        name = request.POST['name']
        subject_id = request.POST['subject']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        allow_calculator = 'allow_calculator' in request.POST

        subject = get_object_or_404(Subject, id=subject_id)
        exam = Exam.objects.create(
            subject=subject,
            name=name,
            start_time=start_time,
            end_time=end_time,
            created_by=request.user,
            allow_calculator=allow_calculator
        )
        return redirect('teacher_exam_detail', exam_id=exam.id)

    return render(request, 'accounts/teacher_create_exam.html', {'courses': courses, 'subjects': subjects})


# ===== Exam Detail & Add Questions =====
@login_required
def teacher_exam_detail(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    questions = Question.objects.filter(exam=exam)

    if request.method == 'POST':
        qtext = request.POST['question_text']
        option1 = request.POST['option1']
        option2 = request.POST['option2']
        option3 = request.POST.get('option3', '')
        option4 = request.POST.get('option4', '')
        correct_option = request.POST['correct_option']

        Question.objects.create(
            exam=exam,
            question_text=qtext,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_option
        )
        return redirect('teacher_exam_detail', exam_id=exam.id)

    return render(request, 'accounts/teacher_exam_detail.html', {'exam': exam, 'questions': questions})


# ===== Student dashboard (ENHANCED) =====
@login_required
def student_dashboard(request):
    exams = Exam.objects.filter(subject__course=request.user.profile.course, is_active=True)
    
    # Calculate statistics
    completed_exams = StudentExam.objects.filter(student=request.user, is_submitted=True)
    completed_count = completed_exams.count()
    
    if completed_count > 0:
        scores = [exam.score for exam in completed_exams if exam.score is not None]
        average_score = round(sum(scores) / len(scores), 1) if scores else 0
    else:
        average_score = 0
    
    pending_count = max(0, exams.count() - completed_count)
    
    context = {
        'exams': exams,
        'completed_count': completed_count,
        'average_score': average_score,
        'pending_count': pending_count,
    }
    
    return render(request, 'accounts/student_dashboard.html', context)


# ===== Take Exam =====
@login_required
def student_take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    profile = request.user.profile

    # Check if exam belongs to student's course
    if exam.course != profile.course:
        return render(request, 'accounts/student_exams.html', {'error': 'You cannot take this exam.'})

    # Get or create StudentExam instance
    student_exam, created = StudentExam.objects.get_or_create(student=request.user, exam=exam)

    questions = Question.objects.filter(exam=exam)
    now = timezone.now()

    # Check if exam is active
    if now < exam.start_time or now > exam.end_time:
        return render(request, 'accounts/student_exams.html', {'error': 'Exam is not active now.'})

    # Handle form submission
    if request.method == 'POST':
        score = 0
        for question in questions:
            answer = request.POST.get(str(question.id))
            if answer == question.correct_option:
                score += 1
        student_exam.score = score
        student_exam.is_submitted = True
        student_exam.save()
        return redirect('student_history')

    # Render exam page
    return render(request, 'accounts/student_exam.html', {'exam': exam, 'questions': questions})


# ===== Student Exam History (ENHANCED) =====
@login_required
def student_history(request):
    records = StudentExam.objects.filter(student=request.user).order_by('-end_time')
    
    # Calculate statistics
    completed_records = records.filter(is_submitted=True)
    
    if completed_records.exists():
        scores = [r.score for r in completed_records if r.score is not None]
        
        if scores:
            average_score = round(sum(scores) / len(scores), 1)
            highest_score = max(scores)
            passing_count = len([s for s in scores if s >= 60])
        else:
            average_score = 0
            highest_score = 0
            passing_count = 0
    else:
        average_score = 0
        highest_score = 0
        passing_count = 0
    
    context = {
        'records': records,
        'average_score': average_score,
        'highest_score': highest_score,
        'passing_count': passing_count,
    }
    
    return render(request, 'accounts/student_history.html', context)


# ===== Teacher Exam Results =====
@login_required
def teacher_exam_results(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    results = Result.objects.filter(exam=exam)
    return render(request, 'accounts/teacher_exam_results.html', {'exam': exam, 'results': results})
