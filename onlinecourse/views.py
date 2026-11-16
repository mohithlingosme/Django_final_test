from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_http_methods

from .forms import ExamSubmissionForm
from .models import Answer, Course, Lesson, Submission


@require_GET
def course_list(request):
    courses = Course.objects.prefetch_related("lessons")
    return render(request, "onlinecourse/course_list.html", {"courses": courses})


@require_GET
def course_details(request, course_id):
    course = get_object_or_404(
        Course.objects.prefetch_related("lessons"),
        pk=course_id,
    )
    return render(
        request,
        "onlinecourse/course_details_bootstrap.html",
        {"course": course},
    )


@login_required
@require_http_methods(["GET", "POST"])
@csrf_protect
def submit(request, lesson_id):
    lesson = get_object_or_404(
        Lesson.objects.select_related("course").prefetch_related(
            "questions__choices"
        ),
        pk=lesson_id,
    )
    questions = list(lesson.questions.all())
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
            form.add_error(None, "This lesson does not have any exam questions.")
        if form.is_valid() and questions:
            selected_choices = {
                choice.pk: choice
                for question in questions
                for choice in question.choices.all()
            }
            answers = [
                (
                    question,
                    selected_choices[
                        int(
                            form.cleaned_data[
                                ExamSubmissionForm.field_name(question.pk)
                            ]
                        )
                    ],
                )
                for question in questions
            ]
            correct_answers = sum(choice.is_correct for _, choice in answers)
            total_questions = len(questions)
            score = correct_answers * 100 // total_questions
            passed = score >= lesson.pass_percentage

            with transaction.atomic():
                submission = Submission.objects.create(
                    student=request.user,
                    lesson=lesson,
                    score=score,
                    correct_answers=correct_answers,
                    total_questions=total_questions,
                    pass_percentage=lesson.pass_percentage,
                    passed=passed,
                )
                Answer.objects.bulk_create(
                    [
                        Answer(
                            submission=submission,
                            question=question,
                            selected_choice=choice,
                            is_correct=choice.is_correct,
                        )
                        for question, choice in answers
                    ]
                )
            return redirect(
                "onlinecourse:show_exam_result",
                submission_id=submission.pk,
            )

        return render(
            request,
            "onlinecourse/exam.html",
            {
                "lesson": lesson,
                "question_fields": question_fields,
                "form": form,
            },
            status=400,
        )

    return render(
        request,
        "onlinecourse/exam.html",
        {
            "lesson": lesson,
            "question_fields": question_fields,
            "form": form,
        },
    )


@login_required
@require_GET
def show_exam_result(request, submission_id):
    submission = get_object_or_404(
        Submission.objects.select_related(
            "lesson",
            "lesson__course",
        ).prefetch_related(
            "answers__question",
            "answers__question__choices",
            "answers__selected_choice",
        ),
        pk=submission_id,
        student=request.user,
    )
    return render(
        request,
        "onlinecourse/exam_result.html",
        {"submission": submission},
    )
