import json
import math
from pathlib import Path


def gcd(a, b):
    return math.gcd(abs(a), abs(b))


def lcm(a, b):
    if a == 0 or b == 0:
        return 0
    g = gcd(a, b)
    return abs(a * b) // g if g else 0


OPS = [
    {
        "op_key": "sum",
        "title": "Sum",
        "difficulty": None,
        "tags": "math, arithmetic",
        "statement": "Given two integers a and b, output their sum.",
        "output_format": "Output a single integer: a+b.",
        "fn": lambda a, b: a + b,
    },
    {
        "op_key": "difference",
        "title": "Difference",
        "tags": "math, arithmetic",
        "statement": "Given two integers a and b, output their difference a-b.",
        "output_format": "Output a single integer: a-b.",
        "fn": lambda a, b: a - b,
    },
    {
        "op_key": "product",
        "title": "Product",
        "tags": "math, arithmetic",
        "statement": "Given two integers a and b, output their product a*b.",
        "output_format": "Output a single integer: a*b.",
        "fn": lambda a, b: a * b,
    },
    {
        "op_key": "max",
        "title": "Maximum",
        "tags": "math, comparisons",
        "statement": "Given two integers a and b, output the larger of the two.",
        "output_format": "Output a single integer: max(a,b).",
        "fn": lambda a, b: max(a, b),
    },
    {
        "op_key": "min",
        "title": "Minimum",
        "tags": "math, comparisons",
        "statement": "Given two integers a and b, output the smaller of the two.",
        "output_format": "Output a single integer: min(a,b).",
        "fn": lambda a, b: min(a, b),
    },
    {
        "op_key": "absdiff",
        "title": "Absolute Difference",
        "tags": "math, absolute",
        "statement": "Given two integers a and b, output |a-b|.",
        "output_format": "Output a single integer: abs(a-b).",
        "fn": lambda a, b: abs(a - b),
    },
    {
        "op_key": "gcd",
        "title": "GCD",
        "tags": "math, number theory",
        "statement": "Given two integers a and b, output their greatest common divisor.",
        "output_format": "Output a single integer: gcd(a,b).",
        "fn": lambda a, b: gcd(a, b),
    },
    {
        "op_key": "lcm",
        "title": "LCM",
        "tags": "math, number theory",
        "statement": "Given two integers a and b, output their least common multiple.",
        "output_format": "Output a single integer: lcm(a,b).",
        "fn": lambda a, b: lcm(a, b),
    },
    {
        "op_key": "square_sum",
        "title": "Square Sum",
        "tags": "math, arithmetic",
        "statement": "Given two integers a and b, output a^2 + b^2.",
        "output_format": "Output a single integer: a*a + b*b.",
        "fn": lambda a, b: a * a + b * b,
    },
    {
        "op_key": "compare",
        "title": "Comparison",
        "tags": "math, comparisons",
        "statement": "Given two integers a and b, output 'Greater' if a>b, 'Less' if a<b, and 'Equal' otherwise.",
        "output_format": "Output one word: Greater, Less, or Equal.",
        "fn": lambda a, b: "Greater" if a > b else ("Less" if a < b else "Equal"),
    },
    {
        "op_key": "parity_sum",
        "title": "Parity of Sum",
        "tags": "math, parity",
        "statement": "Given two integers a and b, output 'Even' if a+b is even, otherwise output 'Odd'.",
        "output_format": "Output one word: Even or Odd.",
        "fn": lambda a, b: "Even" if (a + b) % 2 == 0 else "Odd",
    },
    {
        "op_key": "sign_sum",
        "title": "Sign of Sum",
        "tags": "math, signs",
        "statement": "Given two integers a and b, output 'Positive' if a+b>0, 'Zero' if a+b==0, and 'Negative' otherwise.",
        "output_format": "Output one word: Positive, Zero, or Negative.",
        "fn": lambda a, b: "Positive" if (a + b) > 0 else ("Zero" if (a + b) == 0 else "Negative"),
    },
]


INPUT_FORMAT_2 = "Two integers a and b separated by space."
OUTPUT_FORMAT_INT = "Output a single value for the computed task."
CONSTRAINTS = "-1000000000 <= a,b <= 1000000000"


def make_problem(problem_id_index: int, op, a1, b1, a2, b2, a3, b3, difficulty):
    def fmt(x):
        return str(x)

    t1_in = f"{a1} {b1}"
    t2_in = f"{a2} {b2}"
    t3_in = f"{a3} {b3}"

    t1_out = fmt(op["fn"](a1, b1))
    t2_out = fmt(op["fn"](a2, b2))
    t3_out = fmt(op["fn"](a3, b3))

    title = f"{op['title']} Task #{problem_id_index}"
    statement = op["statement"]

    # Keep statements short but distinct.
    tags = op["tags"]

    return {
        "title": title,
        "statement": statement,
        "input_format": INPUT_FORMAT_2,
        "output_format": op.get("output_format", OUTPUT_FORMAT_INT),
        "constraints": CONSTRAINTS,
        "sample_input": t1_in,
        "sample_output": t1_out,
        "difficulty": difficulty,
        "tags": tags,
        "discussion_count": 0,
        "testcases": [
            {"input": t1_in, "expected_output": t1_out, "is_sample": True, "is_hidden": False, "order": 1},
            {"input": t2_in, "expected_output": t2_out, "is_sample": False, "is_hidden": False, "order": 2},
            {"input": t3_in, "expected_output": t3_out, "is_sample": False, "is_hidden": True, "order": 3},
        ],
    }


def main():
    out_path = Path(__file__).resolve().parent / "problems_seed.json"

    problems = []

    # Problem 1 (must match existing title used by verify_problem_runner)
    problems.append(
        {
            "title": "Sum of Two Integers",
            "statement": "Given two integers a and b, output their sum.",
            "input_format": "Two integers a and b separated by space.",
            "output_format": "Output a single integer: a+b.",
            "constraints": "-1000000000 <= a,b <= 1000000000",
            "sample_input": "3 5",
            "sample_output": "8",
            "difficulty": "easy",
            "tags": "math, arithmetic",
            "discussion_count": 0,
            "testcases": [
                {"input": "3 5", "expected_output": "8", "is_sample": True, "is_hidden": False, "order": 1},
                {"input": "-1 0", "expected_output": "-1", "is_sample": False, "is_hidden": False, "order": 2},
                {"input": "10 12", "expected_output": "22", "is_sample": False, "is_hidden": True, "order": 3},
                {"input": "1000000000 1000000000", "expected_output": "2000000000", "is_sample": False, "is_hidden": True, "order": 4},
                {"input": "-7 -8", "expected_output": "-15", "is_sample": False, "is_hidden": True, "order": 5},
            ],
        }
    )

    # Problem 2
    problems.append(
        {
            "title": "Even or Odd",
            "statement": "Given an integer n, output 'Even' if n is even, otherwise output 'Odd'.",
            "input_format": "Single integer n.",
            "output_format": "Output 'Even' or 'Odd'.",
            "constraints": "-1000000000000000000 <= n <= 1000000000000000000",
            "sample_input": "0",
            "sample_output": "Even",
            "difficulty": "easy",
            "tags": "math, parity",
            "discussion_count": 0,
            "testcases": [
                {"input": "0", "expected_output": "Even", "is_sample": True, "is_hidden": False, "order": 1},
                {"input": "1", "expected_output": "Odd", "is_sample": False, "is_hidden": False, "order": 2},
                {"input": "2", "expected_output": "Even", "is_sample": False, "is_hidden": True, "order": 3},
                {"input": "-1", "expected_output": "Odd", "is_sample": False, "is_hidden": True, "order": 4},
                {"input": "1000000000000000000", "expected_output": "Even", "is_sample": False, "is_hidden": True, "order": 5},
            ],
        }
    )

    a_sample, b_sample = 3, 5
    a_public, b_public = -1, 0
    a_hidden, b_hidden = 1000000000, 1000000000

    # Create remaining 58 problems with exact distribution:
    # Total desired (60): easy=25, medium=25, hard=10
    # First two are already set to "easy", so remaining:
    remaining_easy = 23
    remaining_medium = 25
    remaining_hard = 10

    total = 60
    ops_len = len(OPS)
    idx = 3
    while len(problems) < total:
        op = OPS[(idx - 3) % ops_len]

        if remaining_easy > 0:
            difficulty = "easy"
            remaining_easy -= 1
        elif remaining_medium > 0:
            difficulty = "medium"
            remaining_medium -= 1
        else:
            difficulty = "hard"
            remaining_hard -= 1

        problems.append(
            make_problem(
                problem_id_index=idx,
                op=op,
                a1=a_sample,
                b1=b_sample,
                a2=a_public,
                b2=b_public,
                a3=a_hidden,
                b3=b_hidden,
                difficulty=difficulty,
            )
        )
        idx += 1

    if len(problems) != total:
        raise SystemExit(f"Generator produced {len(problems)} problems, expected {total}.")

    out_path.write_text(json.dumps(problems, indent=2), encoding="utf-8")
    print(f"Wrote {len(problems)} problems to {out_path}")


if __name__ == "__main__":
    main()

