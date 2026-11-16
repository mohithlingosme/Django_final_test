from django.contrib import admin

from .models import (
    Answer,
    Choice,
    Course,
    Enrollment,
    Instructor,
    Learner,
    Lesson,
    Question,
    Submission,
)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    exclude = ("course",)
    show_change_link = True


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    show_change_link = True


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    can_delete = False
    readonly_fields = ("question", "selected_choice", "is_correct")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "pass_percentage", "created_at")
    search_fields = ("title", "description")
    inlines = (LessonInline,)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "pass_percentage")
    list_filter = ("course",)
    search_fields = ("title", "course__title")
    inlines = (QuestionInline,)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "course", "lesson", "grade", "order")
    list_filter = ("course", "lesson")
    search_fields = ("question_text", "course__title", "lesson__title")
    inlines = (ChoiceInline,)


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("text", "question", "is_correct")
    list_filter = ("is_correct", "question__course")
    search_fields = ("text", "question__question_text")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "date_enrolled")
    list_filter = ("course", "date_enrolled")
    search_fields = ("user__username", "course__title")


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ("user", "full_time", "total_learners")
    list_filter = ("full_time",)
    search_fields = ("user__username",)


@admin.register(Learner)
class LearnerAdmin(admin.ModelAdmin):
    list_display = ("user", "occupation", "social_link")
    list_filter = ("occupation",)
    search_fields = ("user__username",)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "enrollment",
        "lesson",
        "score",
        "passed",
        "submitted_at",
    )
    list_filter = ("passed", "enrollment__course")
    search_fields = ("student__username", "enrollment__course__title")
    readonly_fields = (
        "id",
        "enrollment",
        "student",
        "lesson",
        "score",
        "correct_answers",
        "total_questions",
        "pass_percentage",
        "passed",
        "submitted_at",
        "choices",
    )
    inlines = (AnswerInline,)

    def has_add_permission(self, request):
        return False


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("submission", "question", "selected_choice", "is_correct")
    list_filter = ("is_correct",)
    search_fields = ("question__question_text", "submission__student__username")
    readonly_fields = ("submission", "question", "selected_choice", "is_correct")

    def has_add_permission(self, request):
        return False
