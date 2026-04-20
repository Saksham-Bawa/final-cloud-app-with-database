from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Course, Enrollment, Question, Choice, Submission
from django.contrib.auth import login, logout, authenticate
import logging
from django.urls import reverse

logger = logging.getLogger(__name__)


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        from django.contrib.auth.models import User
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name,
                                            last_name=last_name, password=password)
            login(request, user)
            return HttpResponseRedirect(reverse(viewname='onlinecourse:index'))
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse(viewname='onlinecourse:index'))
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return HttpResponseRedirect(reverse(viewname='onlinecourse:index'))


def index(request):
    courses = Course.objects.all()
    context = {"course_list": courses}
    return render(request, 'onlinecourse/course_list_bootstrap.html', context)


def enroll(request, course_id):
    course = Course.objects.get(pk=course_id)
    user = request.user
    is_enrolled = Enrollment.objects.filter(user=user, course=course).exists()
    if not is_enrolled and user.is_authenticated:
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()
    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=[course_id]))


def course_details(request, course_id):
    context = {}
    course = Course.objects.get(pk=course_id)
    context['course'] = course
    user = request.user
    if user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=user, course=course).exists()
        context['is_enrolled'] = is_enrolled
    return render(request, 'onlinecourse/course_details_bootstrap.html', context)


def submit(request, course_id):
    user = request.user
    course = Course.objects.get(pk=course_id)
    enrollment = Enrollment.objects.get(user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    choices = []
    for key, value in request.POST.items():
        if key.startswith('choice'):
            choice_id = int(value)
            choices.append(choice_id)
    for choice_id in choices:
        choice = Choice.objects.get(pk=choice_id)
        submission.choices.add(choice)
    submission.save()
    return HttpResponseRedirect(reverse(viewname='onlinecourse:show_exam_result',
                                        args=[course_id, submission.id]))


def show_exam_result(request, course_id, submission_id):
    context = {}
    course = Course.objects.get(pk=course_id)
    submission = Submission.objects.get(pk=submission_id)
    choices = submission.choices.all()
    total_score = 0
    for lesson in course.lesson_set.all():
        for question in lesson.question_set.all():
            selected_ids = choices.filter(question=question).values_list('id', flat=True)
            if question.is_get_score(selected_ids):
                total_score += question.grade
    context['course'] = course
    context['submission'] = submission
    context['choices'] = choices
    context['total_score'] = total_score
    context['pass'] = total_score >= 80
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
