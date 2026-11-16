from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Answer, Choice, Course, Lesson, Question, Submission


class OnlineCourseViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.student = user_model.objects.create_user(
            username="student",
            password="test-password",
        )
        self.course = Course.objects.create(
            title="Django Basics",
            description="Learn Django.",
        )
        self.lesson = Lesson.objects.create(
            course=self.course,
            title="Models",
            pass_percentage=50,
        )
        self.first_question = Question.objects.create(
            lesson=self.lesson,
            text="Which framework is this?",
            order=1,
        )
        self.first_correct = Choice.objects.create(
            question=self.first_question,
            text="Django",
            is_correct=True,
        )
        Choice.objects.create(
            question=self.first_question,
            text="Flask",
        )
        self.second_question = Question.objects.create(
            lesson=self.lesson,
            text="Which language is Django written in?",
            order=2,
        )
        self.second_correct = Choice.objects.create(
            question=self.second_question,
            text="Python",
            is_correct=True,
        )
        self.second_incorrect = Choice.objects.create(
            question=self.second_question,
            text="Ruby",
        )
        self.client.force_login(self.student)

    def _submit_url(self):
        return reverse("onlinecourse:submit", args=[self.lesson.pk])

    def test_login_route_and_exam_authentication_redirect(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, "Sign in")

        self.client.logout()
        response = self.client.get(self._submit_url())
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={self._submit_url()}",
        )

    def test_admin_index_displays_auth_and_onlinecourse_apps(self):
        admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_login(admin_user)

        response = self.client.get(reverse("admin:index"))

        self.assertContains(response, "Authentication and Authorization")
        self.assertContains(response, "OnlineCourse")

    def test_course_details_renders_lessons_and_empty_state(self):
        response = self.client.get(
            reverse("onlinecourse:course_details", args=[self.course.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.title)
        self.assertContains(response, self.lesson.title)

        empty_course = Course.objects.create(title="Empty course")
        response = self.client.get(
            reverse("onlinecourse:course_details", args=[empty_course.pk])
        )
        self.assertContains(response, "No lessons have been added")

    def test_submission_calculates_score_and_displays_success_result(self):
        response = self.client.post(
            self._submit_url(),
            {
                f"question_{self.first_question.pk}": str(self.first_correct.pk),
                f"question_{self.second_question.pk}": str(
                    self.second_incorrect.pk
                ),
                "score": "100",
                "passed": "false",
            },
        )

        submission = Submission.objects.get()
        self.assertRedirects(
            response,
            reverse(
                "onlinecourse:show_exam_result",
                args=[submission.pk],
            ),
        )
        self.assertEqual(submission.score, 50)
        self.assertEqual(submission.correct_answers, 1)
        self.assertEqual(submission.total_questions, 2)
        self.assertTrue(submission.passed)
        self.assertEqual(Answer.objects.filter(submission=submission).count(), 2)
        result = self.client.get(
            reverse(
                "onlinecourse:show_exam_result",
                args=[submission.pk],
            )
        )
        self.assertContains(result, "Congratulations")
        self.assertContains(result, "50%")
        self.assertContains(result, "Exam results")
        self.assertContains(result, "Correct answer: Python")

    def test_failed_attempt_does_not_display_congratulations(self):
        self.lesson.pass_percentage = 75
        self.lesson.save(update_fields=["pass_percentage"])
        response = self.client.post(
            self._submit_url(),
            {
                f"question_{self.first_question.pk}": str(self.first_correct.pk),
                f"question_{self.second_question.pk}": str(
                    self.second_incorrect.pk
                ),
            },
        )
        submission = Submission.objects.get()

        self.assertFalse(submission.passed)
        self.assertEqual(submission.score, 50)
        result = self.client.get(
            reverse(
                "onlinecourse:show_exam_result",
                args=[submission.pk],
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertNotContains(result, "Congratulations")
        self.assertContains(result, "did not meet the pass mark")

    def test_invalid_or_missing_choices_do_not_create_submission(self):
        invalid_response = self.client.post(
            self._submit_url(),
            {
                f"question_{self.first_question.pk}": str(
                    self.second_correct.pk
                ),
                f"question_{self.second_question.pk}": str(
                    self.second_correct.pk
                ),
            },
        )
        missing_response = self.client.post(
            self._submit_url(),
            {
                f"question_{self.first_question.pk}": str(
                    self.first_correct.pk
                ),
            },
        )

        self.assertEqual(invalid_response.status_code, 400)
        self.assertEqual(missing_response.status_code, 400)
        self.assertFalse(Submission.objects.exists())

    def test_submission_requires_csrf_and_result_is_private(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.student)
        csrf_response = csrf_client.post(
            self._submit_url(),
            {
                f"question_{self.first_question.pk}": str(
                    self.first_correct.pk
                ),
                f"question_{self.second_question.pk}": str(
                    self.second_correct.pk
                ),
            },
        )
        self.assertEqual(csrf_response.status_code, 403)

        submission = Submission.objects.create(
            student=self.student,
            lesson=self.lesson,
            score=100,
            correct_answers=2,
            total_questions=2,
            pass_percentage=50,
            passed=True,
        )
        other_student = get_user_model().objects.create_user(
            username="another-student",
            password="test-password",
        )
        self.client.force_login(other_student)
        response = self.client.get(
            reverse(
                "onlinecourse:show_exam_result",
                args=[submission.pk],
            )
        )

        self.assertEqual(response.status_code, 404)
