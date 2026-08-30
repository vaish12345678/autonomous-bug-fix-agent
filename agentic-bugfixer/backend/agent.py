import os
import re
import json
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is not set in the .env file."
    )

client = genai.Client(api_key=api_key)

MODEL = os.getenv(
    "MODEL_NAME",
    "gemini-2.5-flash"
)


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
BENCHMARKS_DIR = BASE_DIR / "benchmarks"


# ============================================================
# REPOSITORY READER
# ============================================================

def read_repository(repo_path: str) -> str:

    root = Path(repo_path).resolve()

    context = []

    for file in root.rglob("*"):

        if not file.is_file():
            continue

        if ".git" in file.parts:
            continue

        if "__pycache__" in file.parts:
            continue

        if ".pytest_cache" in file.parts:
            continue

        try:

            content = file.read_text(
                encoding="utf-8"
            )

            relative_path = file.relative_to(root)

            context.append(
                f"\n--- {relative_path} ---\n"
                f"{content}"
            )

        except Exception:
            pass

    return "\n".join(context)


# ============================================================
# CLEAN GEMINI RESPONSE
# ============================================================

def clean_response(content: str) -> str:

    if not content:
        return ""

    content = content.strip()

    # Remove Python markdown fences
    content = re.sub(
        r"^```python\s*",
        "",
        content,
        flags=re.IGNORECASE
    )

    # Remove JSON markdown fences
    content = re.sub(
        r"^```json\s*",
        "",
        content,
        flags=re.IGNORECASE
    )

    # Remove generic markdown fences
    content = re.sub(
        r"^```\s*",
        "",
        content
    )

    content = re.sub(
        r"\s*```$",
        "",
        content
    )

    return content.strip()


# ============================================================
# BUG ANALYSIS
# ============================================================

def analyze_bug(
    issue: str,
    repository: str
) -> dict:

    prompt = f"""
You are a senior autonomous software debugging agent.

Analyze the software issue and repository.

ISSUE:
{issue}

REPOSITORY:
{repository}

Determine:

1. The root cause.
2. The exact source file that needs modification.
3. What correction is required.

IMPORTANT:
- Do not modify tests.
- Do not invent files.
- Choose a file that actually exists.
- Do not select a test file.
- Keep the fix minimal.

Return ONLY valid JSON.

Required format:

{{
    "root_cause": "short explanation",
    "file": "relative/path/to/source_file.py",
    "correction": "short explanation"
}}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    text = clean_response(
        response.text
    )

    try:

        result = json.loads(text)

    except json.JSONDecodeError:

        # Try to extract JSON object
        match = re.search(
            r"\{.*\}",
            text,
            re.DOTALL
        )

        if not match:
            raise ValueError(
                "Gemini did not return valid JSON."
            )

        result = json.loads(
            match.group(0)
        )

    required_fields = [
        "root_cause",
        "file",
        "correction"
    ]

    for field in required_fields:

        if field not in result:

            raise ValueError(
                f"Gemini response missing field: {field}"
            )

    return result


# ============================================================
# FILE READER
# ============================================================

def read_file(
    repo_path: str,
    file_name: str
) -> str:

    root = Path(repo_path).resolve()

    file_path = (
        root / file_name
    ).resolve()

    # Security check
    if root not in file_path.parents:

        raise ValueError(
            "Invalid file path."
        )

    if not file_path.is_file():

        raise FileNotFoundError(
            f"Target file does not exist: {file_name}"
        )

    return file_path.read_text(
        encoding="utf-8"
    )


# ============================================================
# VALIDATE TARGET FILE
# ============================================================

def validate_target_file(
    file_name: str
):

    path = Path(file_name)

    file_lower = path.name.lower()

    if file_lower.startswith("test_"):

        raise ValueError(
            "Agent is not allowed to modify test files."
        )

    if file_lower.endswith("_test.py"):

        raise ValueError(
            "Agent is not allowed to modify test files."
        )


# ============================================================
# GENERATE INITIAL FIX
# ============================================================

def generate_fix(
    issue: str,
    repository: str,
    analysis: dict,
    target_file: str
) -> str:

    prompt = f"""
You are an expert software engineer.

Fix the reported bug.

ISSUE:
{issue}

ROOT CAUSE:
{analysis["root_cause"]}

CORRECTION:
{analysis["correction"]}

TARGET FILE:
{target_file}

REPOSITORY:
{repository}

Return ONLY the complete corrected contents
of this source file:

{target_file}

Rules:

- Do not modify tests.
- Do not delete tests.
- Do not add new files.
- Do not add explanations.
- Do not use markdown code fences.
- Preserve existing functionality.
- Make the smallest possible change.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return clean_response(
        response.text
    )


# ============================================================
# UPDATE FILE
# ============================================================

def update_file(
    repo_path: str,
    file_name: str,
    new_content: str
):

    validate_target_file(
        file_name
    )

    root = Path(repo_path).resolve()

    file_path = (
        root / file_name
    ).resolve()

    # Security check
    if root not in file_path.parents:

        raise ValueError(
            "Invalid file path."
        )

    if not file_path.is_file():

        raise FileNotFoundError(
            f"Target file does not exist: {file_name}"
        )

    file_path.write_text(
        new_content.rstrip() + "\n",
        encoding="utf-8"
    )


# ============================================================
# RUN TESTS
# ============================================================

def run_tests(
    repo_path: str
) -> dict:

    print(
        "\n========== RUNNING TESTS ==========\n"
    )

    try:

        result = subprocess.run(
            ["pytest"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=120
        )

        output = (
            result.stdout
            + "\n"
            + result.stderr
        )

        print(output)

        return {
            "passed": result.returncode == 0,
            "output": output
        }

    except subprocess.TimeoutExpired:

        return {
            "passed": False,
            "output": "Tests timed out."
        }

    except Exception as error:

        return {
            "passed": False,
            "output": str(error)
        }


# ============================================================
# GIT DIFF
# ============================================================

def get_git_diff(
    repo_path: str
) -> str:

    try:

        result = subprocess.run(
            ["git", "diff"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )

        return result.stdout.strip()

    except Exception as error:

        return (
            f"Unable to generate git diff: {error}"
        )


# ============================================================
# SELF-CORRECTION
# ============================================================

def repair_fix(
    issue: str,
    repository: str,
    analysis: dict,
    target_file: str,
    current_code: str,
    test_output: str
) -> str:

    prompt = f"""
You are an autonomous software debugging agent.

The previous fix failed the tests.

ORIGINAL ISSUE:
{issue}

ROOT CAUSE:
{analysis["root_cause"]}

CORRECTION:
{analysis["correction"]}

TARGET FILE:
{target_file}

CURRENT CODE:
{current_code}

TEST FAILURE:
{test_output}

Your job is to correct the implementation.

Instructions:

1. Read the test failure carefully.
2. Determine why the previous solution failed.
3. Correct the implementation.
4. Do not modify tests.
5. Do not invent files.
6. Preserve existing functionality.
7. Make the smallest necessary change.
8. Return ONLY the complete corrected contents of:
   {target_file}
9. Do not use markdown code fences.
10. Do not add explanations.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return clean_response(
        response.text
    )


# ============================================================
# LIST BENCHMARKS
# ============================================================

def get_benchmarks():

    if not BENCHMARKS_DIR.exists():

        raise FileNotFoundError(
            f"Benchmarks directory not found: "
            f"{BENCHMARKS_DIR}"
        )

    benchmarks = []

    for directory in BENCHMARKS_DIR.iterdir():

        if not directory.is_dir():
            continue

        if not directory.name.startswith("bug_"):
            continue

        issue_file = directory / "issue.txt"
        repo_directory = directory / "repo"

        if (
            issue_file.is_file()
            and repo_directory.is_dir()
        ):

            benchmarks.append(
                directory
            )

    benchmarks.sort(
        key=lambda path: path.name
    )

    return benchmarks


# ============================================================
# SELECT BENCHMARK
# ============================================================

def select_benchmark():

    benchmarks = get_benchmarks()

    if not benchmarks:

        raise RuntimeError(
            "No valid benchmarks found."
        )

    print(
        "\n========== AVAILABLE BUGS ==========\n"
    )

    for index, benchmark in enumerate(
        benchmarks,
        start=1
    ):

        print(
            f"{index}. {benchmark.name}"
        )

    print()

    while True:

        choice = input(
            "Select bug number: "
        ).strip()

        try:

            number = int(choice)

            if 1 <= number <= len(benchmarks):

                return benchmarks[
                    number - 1
                ]

        except ValueError:
            pass

        print(
            "Invalid choice. Please try again."
        )


# ============================================================
# MAIN AGENT
# ============================================================

def main():

    print(
        "\n========================================"
    )

    print(
        "🤖 AUTONOMOUS BUG FIX AGENT"
    )

    print(
        "========================================"
    )

    # --------------------------------------------------------
    # SELECT BUG
    # --------------------------------------------------------

    benchmark = select_benchmark()

    repo_path = (
        benchmark / "repo"
    )

    issue_path = (
        benchmark / "issue.txt"
    )

    print(
        f"\nSelected benchmark: {benchmark.name}"
    )

    print(
        f"Repository: {repo_path}"
    )

    print(
        f"Issue: {issue_path}"
    )

    # --------------------------------------------------------
    # READ ISSUE
    # --------------------------------------------------------

    issue = issue_path.read_text(
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # READ REPOSITORY
    # --------------------------------------------------------

    print(
        "\n========== READING REPOSITORY ==========\n"
    )

    repository = read_repository(
        str(repo_path)
    )

    # --------------------------------------------------------
    # ANALYZE BUG
    # --------------------------------------------------------

    print(
        "\n========== ANALYZING BUG ==========\n"
    )

    analysis = analyze_bug(
        issue,
        repository
    )

    print(
        "Root cause:",
        analysis["root_cause"]
    )

    print(
        "File:",
        analysis["file"]
    )

    print(
        "Correction:",
        analysis["correction"]
    )

    # --------------------------------------------------------
    # TARGET FILE
    # --------------------------------------------------------

    target_file = analysis["file"]

    validate_target_file(
        target_file
    )

    current_code = read_file(
        str(repo_path),
        target_file
    )

    # --------------------------------------------------------
    # AGENT LOOP
    # --------------------------------------------------------

    max_attempts = 3

    test_result = None

    for attempt in range(
        1,
        max_attempts + 1
    ):

        print(
            f"\n========== ATTEMPT "
            f"{attempt}/{max_attempts} ==========\n"
        )

        # ----------------------------------------------------
        # INITIAL FIX
        # ----------------------------------------------------

        if attempt == 1:

            print(
                "\n========== GENERATING INITIAL FIX ==========\n"
            )

            fixed_code = generate_fix(
                issue,
                repository,
                analysis,
                target_file
            )

        # ----------------------------------------------------
        # SELF-CORRECTION
        # ----------------------------------------------------

        else:

            print(
                "\n========== SELF-CORRECTION ==========\n"
            )

            print(
                "🤖 Agent is analyzing "
                "the previous test failure..."
            )

            fixed_code = repair_fix(
                issue,
                repository,
                analysis,
                target_file,
                current_code,
                test_result["output"]
            )

        # ----------------------------------------------------
        # CLEAN RESPONSE
        # ----------------------------------------------------

        fixed_code = clean_response(
            fixed_code
        )

        # ----------------------------------------------------
        # SHOW PROPOSED CODE
        # ----------------------------------------------------

        print(
            "\n========== PROPOSED CODE ==========\n"
        )

        print(
            fixed_code
        )

        # ----------------------------------------------------
        # APPLY FIX
        # ----------------------------------------------------

        print(
            "\n========== APPLYING FIX ==========\n"
        )

        update_file(
            str(repo_path),
            target_file,
            fixed_code
        )

        print(
            f"✓ Fix applied to {target_file}"
        )

        # ----------------------------------------------------
        # SHOW DIFF
        # ----------------------------------------------------

        print(
            "\n========== GENERATED DIFF ==========\n"
        )

        diff = get_git_diff(
            str(repo_path)
        )

        if diff:

            print(diff)

        else:

            print(
                "No git changes detected."
            )

        # ----------------------------------------------------
        # RUN TESTS
        # ----------------------------------------------------

        test_result = run_tests(
            str(repo_path)
        )

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        if test_result["passed"]:

            print(
                "\n========================================"
            )

            print(
                "🎉 VERIFIED FIX"
            )

            print(
                f"✓ Tests passed on attempt {attempt}"
            )

            print(
                f"✓ Target file: {target_file}"
            )

            print(
                "========================================"
            )

            return

        # ----------------------------------------------------
        # FAILURE
        # ----------------------------------------------------

        print(
            "\n❌ Tests failed."
        )

        # Read latest modified code
        current_code = read_file(
            str(repo_path),
            target_file
        )

        # ----------------------------------------------------
        # MAX ATTEMPTS
        # ----------------------------------------------------

        if attempt == max_attempts:

            print(
                "\n========================================"
            )

            print(
                "❌ FIX NOT VERIFIED"
            )

            print(
                "Maximum attempts reached."
            )

            print(
                "========================================"
            )

            return


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()