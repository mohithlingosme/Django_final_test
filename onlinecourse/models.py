import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Instructor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="instructor_profiles",
    )
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class Learner(models.Model):
    STUDENT = "student"
    DEVELOPER = "developer"
    DATA_SCIENTIST = "data_scientist"
    DATABASE_ADMIN = "dba"

    OCCUPATION_CHOICES = [
        (STUDENT, "Student"),
        (DEVELOPER, "Developer"),
        (DATA_SCIENTIST, "Data Scientist"),
        (DATABASE_ADMIN, "Database Admin"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="learner_profiles",
    )
    occupation = models.CharField(
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT,
    )
    social_link = models.URLField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.user.username}, {self.occupation}"


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pass_percentage = models.PositiveSmallIntegerField(
        default=70,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
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


class Enrollment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_enrollments",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    date_enrolled = models.DateField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                name="unique_user_course_enrollment",
            ),
        ]
        ordering = ["-date_enrolled", "-pk"]

    def __str__(self):
        return f"{self.user} — {self.course}"


class Question(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="questions",
        null=True,
        blank=True,
    )
    question_text = models.TextField(
        max_length=300,
        verbose_name="Question Text",
    )
    grade = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "pk"]

    def save(self, *args, **kwargs):
        # A lesson belongs to exactly one course. Keep the direct course
        # relationship synchronized when a question is attached to a lesson.
        if self.lesson_id:
            lesson_course_id = self.lesson.course_id
            if self.course_id and self.course_id != lesson_course_id:
                raise ValidationError(
                    "The question's course must match the selected lesson's course."
                )
            self.course_id = lesson_course_id
        super().save(*args, **kwargs)

    def is_get_score(self, selected_ids):
        """Return True only when all and only the correct choices were selected."""
        if hasattr(selected_ids, "values_list"):
            selected_choice_ids = set(
                selected_ids.values_list("pk", flat=True)
            )
        else:
            selected_choice_ids = {
                getattr(choice, "pk", choice) for choice in selected_ids
            }

        correct_choice_ids = set(
            self.choices.filter(is_correct=True).values_list("pk", flat=True)
        )
        return bool(correct_choice_ids) and (
            selected_choice_ids == correct_choice_ids
        )

    @property
    def text(self):
        """Backward-compatible read alias for templates using question.text."""
        return self.question_text

    def __str__(self):
        return self.question_text


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
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    choices = models.ManyToManyField(
        Choice,
        related_name="submissions",
        blank=True,
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exam_submissions",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="submissions",
        null=True,
        blank=True,
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
        return f"{self.student} - {self.enrollment.course} ({self.score}%)"


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
