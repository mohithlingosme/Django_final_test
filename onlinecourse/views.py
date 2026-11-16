from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_http_methods

from .forms import ExamSubmissionForm
from .models import Answer, Course, Enrollment, Lesson, Submission


@require_GET
def course_list(request):
    courses = Course.objects.prefetch_related("lessons")
    return render(request, "onlinecourse/course_list.html", {"courses": courses})


@require_GET
def course_details(request, course_id):
    course = get_object_or_404(
        Course.objects.prefetch_related("lessons", "questions__choices"),
        pk=course_id,
    )
    enrollment = None
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(
            user=request.user,
            course=course,
        ).first()

    return render(
        request,
        "onlinecourse/course_details_bootstrap.html",
        {"course": course, "enrollment": enrollment},
    )


@login_required
@require_http_methods(["GET", "POST"])
@csrf_protect
def submit(request, course_id):
    """Collect course answers, calculate a weighted score and save a submission."""
    course = get_object_or_404(
        Course.objects.prefetch_related("questions__choices", "lessons"),
        pk=course_id,
    )
    questions = list(course.questions.all())
    form = ExamSubmissionForm(
        questions,
        data=request.POST if request.method == "POST" else None,
    )
    question_fields = [
        (question, form[ExamSubmissionForm.field_name(question.pk)])
        for question in questions
    ]

    if request.method == "POST":
        if not questions:
            form.add_error(None, "This course does not have any exam questions.")

        if form.is_valid() and questions:
            selected_choices = []
            question_results = []

            for question in questions:
                selected_choice_id = int(
                    form.cleaned_data[
                        ExamSubmissionForm.field_name(question.pk)
                    ]
                )
                choice = question.choices.get(pk=selected_choice_id)
                selected_choices.append(choice)
                is_correct = question.is_get_score([choice])
                question_results.append((question, choice, is_correct))

            correct_answers = sum(
                1 for _, _, is_correct in question_results if is_correct
            )
            total_questions = len(questions)
            total_points = sum(question.grade for question in questions)
            earned_points = sum(
                question.grade
                for question, _, is_correct in question_results
                if is_correct
            )
            score = (
                round(earned_points * 100 / total_points)
                if total_points
                else 0
            )

            # Preserve a lesson-specific pass mark when all exam questions
            # belong to one lesson; otherwise use the course pass mark.
            lesson_ids = {
                question.lesson_id
                for question in questions
                if question.lesson_id is not None
            }
            result_lesson = (
                Lesson.objects.get(pk=next(iter(lesson_ids)))
                if len(lesson_ids) == 1
                else None
            )
            pass_percentage = (
                result_lesson.pass_percentage
                if result_lesson is not None
                else course.pass_percentage
            )
            passed = score >= pass_percentage

            with transaction.atomic():
                enrollment, _ = Enrollment.objects.get_or_create(
                    user=request.user,
                    course=course,
                )
                submission = Submission.objects.create(
                    enrollment=enrollment,
                    student=request.user,
                    lesson=result_lesson,
                    score=score,
                    correct_answers=correct_answers,
                    total_questions=total_questions,
                    pass_percentage=pass_percentage,
                    passed=passed,
                )
                submission.choices.set(selected_choices)
                Answer.objects.bulk_create(
                    [
                        Answer(
                            submission=submission,
                            question=question,
                            selected_choice=choice,
                            is_correct=is_correct,
                        )
                        for question, choice, is_correct in question_results
                    ]
                )

            return redirect(
                "onlinecourse:show_exam_result",
                course_id=course.pk,
                submission_id=submission.pk,
            )

        return render(
            request,
            "onlinecourse/exam.html",
            {
                "course": course,
                "question_fields": question_fields,
                "form": form,
            },
            status=400,
        )

    return render(
        request,
        "onlinecourse/exam.html",
        {
            "course": course,
            "question_fields": question_fields,
            "form": form,
        },
    )


@login_required
@require_GET
def show_exam_result(request, course_id, submission_id):
    """Show the grade and per-question results for the learner's submission."""
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(
        Submission.objects.select_related(
            "lesson",
            "enrollment",
            "enrollment__course",
            "student",
        ).prefetch_related(
            "answers__question",
            "answers__question__choices",
            "answers__selected_choice",
            "choices",
        ),
        pk=submission_id,
        enrollment__course=course,
        student=request.user,
    )
    return render(
        request,
        "onlinecourse/exam_result.html",
        {
            "course": course,
            "submission": submission,
            "selected_ids": submission.choices.all(),
            "grade": submission.score,
        },
    )
