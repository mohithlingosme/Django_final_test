import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title", "pk"]

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    pass_percentage = models.PositiveSmallIntegerField(
        default=70,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    class Meta:
        ordering = ["order", "pk"]

    def __str__(self):
        return f"{self.course}: {self.title}"


class Question(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "pk"]

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
    )
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.text


class Submission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exam_submissions",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    correct_answers = models.PositiveIntegerField()
    total_questions = models.PositiveIntegerField()
    pass_percentage = models.PositiveSmallIntegerField()
    passed = models.BooleanField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at", "-pk"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(score__lte=100),
                name="submission_score_at_most_100",
            ),
            models.CheckConstraint(
                condition=models.Q(pass_percentage__lte=100),
                name="submission_pass_percentage_at_most_100",
            ),
        ]

    def __str__(self):
        return f"{self.student} - {self.lesson} ({self.score}%)"


class Answer(models.Model):
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.PROTECT,
        related_name="submitted_answers",
    )
    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.PROTECT,
        related_name="submitted_answers",
    )
    is_correct = models.BooleanField()

    class Meta:
        ordering = ["question__order", "question_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["submission", "question"],
                name="one_answer_per_question_per_submission",
            ),
        ]

    def __str__(self):
        return f"{self.question}: {self.selected_choice}"
