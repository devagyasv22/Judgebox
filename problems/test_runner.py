import subprocess
import os
import uuid
from pathlib import Path
from django.conf import settings
from .testcases_model import TestCase

def run_test_cases(language, code, problem_id):
    # Prefer DB-based testcases (seeded via management command/JSON).
    # Fall back to the legacy file-based testcases if DB has none for this problem.
    db_testcases = list(TestCase.objects.filter(problem_id=problem_id).order_by("order", "id"))

    results = []
    i = 1
    workdir_str = getattr(settings, 'SUBMISSION_WORKDIR', '/tmp/judgebox')
    uid = str(uuid.uuid4())
    BASE = Path(workdir_str) / uid
    BASE.mkdir(parents=True, exist_ok=True)

    if language == 'cpp':
        ext = 'cpp'
        source_path = BASE / f"temp_{uid}.cpp"
        executable_path = BASE / f"temp_{uid}_exec"
        source_path.write_text(code)

        compile_result = subprocess.run(['g++', str(source_path), '-o', str(executable_path)], capture_output=True)
        if compile_result.returncode != 0:
            return [{
                'testcase': 0,
                'passed': False,
                'error': compile_result.stderr.decode()
            }]

    elif language == 'java':
        ext = 'java'
        class_name = f"Main{uid.replace('-', '')}"
        code = code.replace('class Main', f'class {class_name}')
        source_path = BASE / f"{class_name}.java"
        source_path.write_text(code)

        compile_result = subprocess.run(['javac', str(source_path)], capture_output=True)
        if compile_result.returncode != 0:
            return [{
                'testcase': 0,
                'passed': False,
                'error': compile_result.stderr.decode()
            }]

    else: 
        ext = 'py'
        source_path = BASE / f"temp_{uid}.py"
        source_path.write_text(code)

    def _judge_one(input_text: str, expected_text: str):
        nonlocal i
        try:
            if language == "cpp":
                result = subprocess.run(
                    [str(executable_path)],
                    input=input_text,
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
            elif language == "java":
                result = subprocess.run(
                    ["java", "-cp", str(BASE), class_name],
                    input=input_text,
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
            else:
                result = subprocess.run(
                    ["python3", str(source_path)],
                    input=input_text,
                    capture_output=True,
                    text=True,
                    timeout=2,
                )

            actual_output = (result.stdout or "").strip()
            expected_output = (expected_text or "").strip()
            results.append(
                {
                    "testcase": i,
                    "passed": actual_output == expected_output,
                    "expected": expected_output,
                    "actual": actual_output,
                }
            )
        except subprocess.TimeoutExpired:
            results.append({"testcase": i, "passed": False, "error": "Time Limit Exceeded"})
        i += 1

    if db_testcases:
        for tc in db_testcases:
            _judge_one(tc.input_data or "", tc.expected_output or "")
        return results

    # Legacy file-based mode
    test_case_dir = os.path.join(
        os.path.dirname(__file__), "testcases", f"problem_{problem_id}"
    )
    while True:
        input_file = os.path.join(test_case_dir, f"input{i}.txt")
        output_file = os.path.join(test_case_dir, f"output{i}.txt")

        if not os.path.exists(input_file) or not os.path.exists(output_file):
            break

        with open(input_file, "r") as f_in:
            expected_output = open(output_file, "r").read().strip()
            _judge_one(f_in.read(), expected_output)

    return results
