from django.contrib import admin
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 5


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 4


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]


class LessonAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]


class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ['name', 'pub_date']
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


class LearnerAdmin(admin.ModelAdmin):
    list_display = ['user', 'occupation', 'social_link']


admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner, LearnerAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission)
