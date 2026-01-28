from django.db import models
from django.contrib.auth.models import User
from django import forms


# ===== Profile for role management =====
class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    approved = models.BooleanField(default=True)
    roll_number = models.CharField(max_length=20, blank=True, null=True)
    course = models.ForeignKey('Course', on_delete=models.SET_NULL, blank=True, null=True)
    is_teacher = models.BooleanField(default=False)


    def __str__(self):
        return self.user.username


# ===== Courses =====
class Course(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ===== Subjects =====
class Subject(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.course.name})"


# ===== Exams =====
class Exam(models.Model):
    
    name = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  # teacher
    is_active = models.BooleanField(default=True)
    allow_calculator = models.BooleanField(default=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=1)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, )
    def __str__(self):
        return f"{self.name} - {self.subject.name}"


# ===== Questions =====
class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question_text = models.TextField()
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200, blank=True, null=True)
    option4 = models.CharField(max_length=200, blank=True, null=True)
    correct_option = models.CharField(max_length=10)  # 'option1', 'option2', etc

    def __str__(self):
        return self.question_text


# ===== Track student exams =====
class StudentExam(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    score = models.FloatField(blank=True, null=True)
    is_submitted = models.BooleanField(default=False)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.username} - {self.exam.name}"


#======== trackresult=======

class Result(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    score = models.FloatField(default=0)
    attempted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.exam.name} - {self.score}"
    

   



class StudentRegistrationForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']  # and password confirmation

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            Profile.objects.create(user=user, course=self.cleaned_data['course'])
        return user
