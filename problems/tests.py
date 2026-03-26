from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from compiler.models import CodeSubmission
from problems.models import Problem
from problems.testcases_model import TestCase as ProblemTestCase


class ProblemsAuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass12345")

        self.problem = Problem.objects.create(
            title="Sum of Two Integers",
            slug="sum-of-two-integers-test",
            statement="Given two integers a and b, output their sum.",
            input_format="Two integers a and b separated by space.",
            output_format="Output a single integer: a+b.",
            constraints="-1000000000 <= a,b <= 1000000000",
            sample_input="3 5",
            sample_output="8",
            difficulty="easy",
            tags="math, arithmetic",
            discussion_count=0,
        )

        ProblemTestCase.objects.create(
            problem=self.problem,
            order=1,
            is_sample=True,
            is_hidden=False,
            input_data="3 5",
            expected_output="8",
        )
        ProblemTestCase.objects.create(
            problem=self.problem,
            order=2,
            is_sample=False,
            is_hidden=False,
            input_data="-1 0",
            expected_output="-1",
        )

    def test_anonymous_problem_list_and_detail_accessible(self):
        resp = self.client.get("/problems/")
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(f"/problems/{self.problem.id}/")
        self.assertEqual(resp.status_code, 200)

    def test_anonymous_submit_redirects_to_login(self):
        resp = self.client.get(f"/problems/{self.problem.id}/submit/")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp["Location"])

        resp = self.client.post(
            f"/problems/{self.problem.id}/submit/",
            data={"language": "py", "code": "print(1)", "input_data": "", "action": "run_all"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp["Location"])

    def test_logged_in_user_can_submit_and_get_results(self):
        self.client.login(username="tester", password="pass12345")

        resp = self.client.get(f"/problems/{self.problem.id}/submit/")
        self.assertEqual(resp.status_code, 200)

        code = "a,b = map(int, input().split())\nprint(a+b)\n"
        resp = self.client.post(
            f"/problems/{self.problem.id}/submit/",
            data={
                "language": "py",
                "code": code,
                "input_data": "",
                "action": "run_all",
            },
        )
        self.assertEqual(resp.status_code, 200)

        # The view should persist a CodeSubmission row.
        self.assertTrue(CodeSubmission.objects.filter(problem=self.problem).exists())

