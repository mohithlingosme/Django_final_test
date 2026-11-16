import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


def backfill_course_enrollment_and_choices(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Question = apps.get_model("onlinecourse", "Question")
    Lesson = apps.get_model("onlinecourse", "Lesson")
    Enrollment = apps.get_model("onlinecourse", "Enrollment")
    Submission = apps.get_model("onlinecourse", "Submission")
    Answer = apps.get_model("onlinecourse", "Answer")

    for question in Question.objects.using(db_alias).all().iterator():
        if question.lesson_id:
            lesson = Lesson.objects.using(db_alias).get(pk=question.lesson_id)
            question.course_id = lesson.course_id
            question.save(using=db_alias, update_fields=["course"])

    for submission in Submission.objects.using(db_alias).all().iterator():
        if not submission.lesson_id:
            continue

        lesson = Lesson.objects.using(db_alias).get(pk=submission.lesson_id)
        enrollment, _ = Enrollment.objects.using(db_alias).get_or_create(
            user_id=submission.student_id,
            course_id=lesson.course_id,
        )
        submission.enrollment_id = enrollment.pk
        submission.save(using=db_alias, update_fields=["enrollment"])

        selected_choice_ids = Answer.objects.using(db_alias).filter(
            submission_id=submission.pk
        ).values_list("selected_choice_id", flat=True)
        submission.choices.set(selected_choice_ids)


class Migration(migrations.Migration):

    dependencies = [
        ("onlinecourse", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Instructor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("full_time", models.BooleanField(default=True)),
                ("total_learners", models.IntegerField(default=0)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="instructor_profiles",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Learner",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "occupation",
                    models.CharField(
                        choices=[
                            ("student", "Student"),
                            ("developer", "Developer"),
                            ("data_scientist", "Data Scientist"),
                            ("dba", "Database Admin"),
                        ],
                        default="student",
                        max_length=20,
                    ),
                ),
                ("social_link", models.URLField(blank=True, max_length=200)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="learner_profiles",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Enrollment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date_enrolled",
                    models.DateField(default=django.utils.timezone.now),
                ),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="enrollments",
                        to="onlinecourse.course",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="course_enrollments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-date_enrolled", "-pk"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("user", "course"),
                        name="unique_user_course_enrollment",
                    ),
                ],
            },
        ),
        migrations.AddField(
            model_name="course",
            name="pass_percentage",
            field=models.PositiveSmallIntegerField(
                default=70,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(100),
                ],
            ),
        ),
        migrations.RenameField(
            model_name="question",
            old_name="text",
            new_name="question_text",
        ),
        migrations.AddField(
            model_name="question",
            name="grade",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="question",
            name="course",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="questions",
                to="onlinecourse.course",
            ),
        ),
        migrations.AlterField(
            model_name="question",
            name="lesson",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="questions",
                to="onlinecourse.lesson",
            ),
        ),
        migrations.AlterField(
            model_name="submission",
            name="lesson",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="submissions",
                to="onlinecourse.lesson",
            ),
        ),
        migrations.AddField(
            model_name="submission",
            name="enrollment",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="submissions",
                to="onlinecourse.enrollment",
            ),
        ),
        migrations.AddField(
            model_name="submission",
            name="choices",
            field=models.ManyToManyField(
                blank=True,
                related_name="submissions",
                to="onlinecourse.choice",
            ),
        ),
        migrations.RunPython(
            backfill_course_enrollment_and_choices,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="question",
            name="course",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="questions",
                to="onlinecourse.course",
            ),
        ),
        migrations.AlterField(
            model_name="submission",
            name="enrollment",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="submissions",
                to="onlinecourse.enrollment",
            ),
        ),
    ]
