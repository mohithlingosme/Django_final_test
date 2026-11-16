from django.contrib import admin

from .models import Answer, Choice, Course, Lesson, Question, Submission


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
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
    list_display = ("title", "created_at")
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
    list_display = ("text", "lesson", "order")
    list_filter = ("lesson__course",)
    search_fields = ("text", "lesson__title", "lesson__course__title")
    inlines = (ChoiceInline,)


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("text", "question", "is_correct")
    list_filter = ("is_correct", "question__lesson__course")
    search_fields = ("text", "question__text")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "lesson",
        "score",
        "passed",
        "submitted_at",
    )
    list_filter = ("passed", "lesson__course")
    search_fields = ("student__username", "lesson__title")
    readonly_fields = (
        "id",
        "student",
        "lesson",
        "score",
        "correct_answers",
        "total_questions",
        "pass_percentage",
        "passed",
        "submitted_at",
    )
    inlines = (AnswerInline,)

    def has_add_permission(self, request):
        return False
