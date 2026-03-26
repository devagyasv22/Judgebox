from django.shortcuts import render, redirect
from .forms import CodeSubmissionForm
from .models import CodeSubmission
from problems.models import Problem
import uuid, subprocess
from pathlib import Path
from django.conf import settings
from django.shortcuts import render, get_object_or_404


def submit_code(request):
    if request.method == 'POST':
        form = CodeSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.output_data = run_code(
                submission.language, submission.code, submission.input_data
            )
            submission.save()
            return render(request, 'compiler/result.html', {'submission': submission})
    else:
        form = CodeSubmissionForm()
    return render(request, 'compiler/submit.html', {'form': form})

def result_page(request):
    return render(request, 'compiler/result.html')

def run_code(language, code, input_data):
    workdir_str = getattr(settings, 'SUBMISSION_WORKDIR', '/tmp/judgebox')
    uid = str(uuid.uuid4())
    BASE = Path(workdir_str) / uid
    BASE.mkdir(parents=True, exist_ok=True)

    ext = 'cpp' if language == 'cpp' else 'py' if language == 'py' else 'java'
    code_path = BASE / f"temp_{uid}.{ext}"
    input_path = BASE / f"input_{uid}.txt"
    output_path = BASE / f"output_{uid}.txt"

    input_path.write_text(input_data or "")

    try:
        if language == 'cpp':
            code_path.write_text(code)
            exe_path = BASE / f"prog_{uid}"
            compile_proc = subprocess.run(
                ['g++', str(code_path), '-o', str(exe_path)],
                timeout=3
            )
            if compile_proc.returncode != 0:
                return "Compilation Error"

            with open(input_path, 'r') as f_in, open(output_path, 'w') as f_out:
                subprocess.run([str(exe_path)], stdin=f_in, stdout=f_out, timeout=3)

        elif language == 'py':
            code_path.write_text(code)
            with open(input_path, 'r') as f_in, open(output_path, 'w') as f_out:
                subprocess.run(
                    ['python3', str(code_path)],
                    stdin=f_in, stdout=f_out, timeout=3
                )

        elif language == 'java':
            java_file = BASE / f"Main_{uid}.java"
            java_file.write_text(code)

            compile_proc = subprocess.run(
                ['javac', str(java_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=3
            )
            if compile_proc.returncode != 0:
                return f"Compilation Error:\n{compile_proc.stderr}"

            with open(input_path, 'r') as f_in, open(output_path, 'w') as f_out:
                subprocess.run(
                    ['java', '-cp', str(BASE), f"Main_{uid}"],
                    stdin=f_in, stdout=f_out, timeout=3
                )

        return output_path.read_text()

    except subprocess.TimeoutExpired:
        return "Time Limit Exceeded"
