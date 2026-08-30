# import os
# import re
# import json
# import time
# import subprocess
# from pathlib import Path

# from dotenv import load_dotenv
# from google import genai

# from backend.patcher import (
#     validate_target_file,
#     create_backup,
#     apply_fix,
#     restore_backup,
#     remove_backup,
#     get_diff,
# )


# # ============================================================
# # CONFIGURATION
# # ============================================================

# load_dotenv()

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# if not GEMINI_API_KEY:
#     raise ValueError(
#         "GEMINI_API_KEY is not set in the .env file."
#     )

# client = genai.Client(
#     api_key=GEMINI_API_KEY
# )

# MODEL = os.getenv(
#     "MODEL_NAME",
#     "gemini-2.5-flash-lite"
# )

# MAX_AI_RETRIES = int(
#     os.getenv("MAX_AI_RETRIES", "3")
# )

# AI_RETRY_DELAY = float(
#     os.getenv("AI_RETRY_DELAY", "5")
# )


# # ============================================================
# # PATH CONFIGURATION
# # ============================================================

# BASE_DIR = Path(__file__).resolve().parent.parent

# BENCHMARKS_DIR = BASE_DIR / "benchmarks"


# # ============================================================
# # AI REQUEST LAYER
# # ============================================================

# def ask_ai(prompt: str) -> str:
#     """
#     Centralized AI request layer.

#     The agent does not contain benchmark-specific solutions.
#     All analysis, code generation and repair decisions are
#     delegated to the configured AI model.
#     """

#     last_error = None

#     for attempt in range(1, MAX_AI_RETRIES + 1):

#         try:

#             print(
#                 f"\n🤖 AI request "
#                 f"({attempt}/{MAX_AI_RETRIES})..."
#             )

#             response = client.models.generate_content(
#                 model=MODEL,
#                 contents=prompt
#             )

#             if not response:
#                 raise RuntimeError(
#                     "AI returned no response."
#                 )

#             if not response.text:
#                 raise RuntimeError(
#                     "AI returned an empty response."
#                 )

#             return response.text.strip()

#         except Exception as error:

#             last_error = error

#             print(
#                 f"\n⚠ AI request failed: {error}"
#             )

#             if attempt < MAX_AI_RETRIES:

#                 wait_time = AI_RETRY_DELAY * attempt

#                 print(
#                     f"⏳ Retrying in "
#                     f"{wait_time:.1f} seconds..."
#                 )

#                 time.sleep(wait_time)

#     raise RuntimeError(
#         f"AI request failed after "
#         f"{MAX_AI_RETRIES} attempts: "
#         f"{last_error}"
#     )


# # ============================================================
# # CLEAN AI RESPONSE
# # ============================================================

# def clean_response(content: str) -> str:

#     if not content:
#         return ""

#     content = content.strip()

#     # Remove markdown code fences.

#     content = re.sub(
#         r"^```(?:python|json|text)?\s*",
#         "",
#         content,
#         flags=re.IGNORECASE
#     )

#     content = re.sub(
#         r"\s*```$",
#         "",
#         content
#     )

#     return content.strip()


# # ============================================================
# # READ REPOSITORY
# # ============================================================

# def read_repository(
#     repo_path: str
# ) -> str:

#     root = Path(repo_path).resolve()

#     if not root.is_dir():
#         raise FileNotFoundError(
#             f"Repository not found: {repo_path}"
#         )

#     ignored_directories = {
#         ".git",
#         "__pycache__",
#         ".pytest_cache",
#         "node_modules",
#         ".venv",
#         "venv",
#         "dist",
#         "build"
#     }

#     supported_extensions = {
#         ".py",
#         ".js",
#         ".jsx",
#         ".ts",
#         ".tsx",
#         ".java",
#         ".cpp",
#         ".c",
#         ".h",
#         ".cs",
#         ".go",
#         ".rs",
#         ".rb",
#         ".php",
#         ".sql",
#         ".json",
#         ".yaml",
#         ".yml",
#         ".toml",
#         ".md",
#         ".txt"
#     }

#     files = []

#     for path in root.rglob("*"):

#         if not path.is_file():
#             continue

#         if any(
#             part in ignored_directories
#             for part in path.parts
#         ):
#             continue

#         if path.suffix.lower() not in supported_extensions:
#             continue

#         try:

#             content = path.read_text(
#                 encoding="utf-8"
#             )

#         except (UnicodeDecodeError, OSError):

#             continue

#         relative_path = path.relative_to(root)

#         files.append(
#             f"\n===== FILE: {relative_path} =====\n"
#             f"{content}"
#         )

#     return "\n".join(files)


# # ============================================================
# # BUG ANALYSIS
# # ============================================================

# def analyze_bug(
#     issue: str,
#     repository: str
# ) -> dict:

#     prompt = f"""
# You are an autonomous senior software debugging agent.

# You must investigate a real software repository and
# determine the actual root cause of the reported issue.

# Do NOT rely on benchmark names.

# Do NOT assume a known bug pattern.

# Reason entirely from the issue and repository contents.

# ============================================================
# ISSUE
# ============================================================

# {issue}

# ============================================================
# REPOSITORY
# ============================================================

# {repository}

# ============================================================
# TASK
# ============================================================

# Analyze the repository carefully.

# 1. Understand the reported issue.
# 2. Inspect the relevant source files.
# 3. Inspect tests when useful.
# 4. Determine the expected behavior.
# 5. Determine the actual behavior.
# 6. Identify the exact root cause.
# 7. Identify the exact source file that must be modified.
# 8. Describe the smallest correct correction.

# ============================================================
# STRICT RULES
# ============================================================

# - Do not modify tests.
# - Do not select a test file.
# - Do not invent files.
# - Select only a file that exists in the repository.
# - Do not hardcode benchmark-specific solutions.
# - Do not assume a particular filename.
# - Do not assume a particular bug pattern.
# - The solution must generalize to valid inputs.
# - Preserve existing APIs unless the issue requires otherwise.
# - Keep the eventual change minimal.

# Return ONLY valid JSON.

# Required format:

# {{
#     "root_cause": "actual defect",
#     "file": "relative/path/to/source/file",
#     "correction": "precise correction"
# }}
# """

#     text = ask_ai(prompt)

#     text = clean_response(text)

#     try:

#         result = json.loads(text)

#     except json.JSONDecodeError:

#         match = re.search(
#             r"\{.*\}",
#             text,
#             re.DOTALL
#         )

#         if not match:
#             raise ValueError(
#                 "AI did not return valid JSON."
#             )

#         result = json.loads(
#             match.group(0)
#         )

#     required_fields = [
#         "root_cause",
#         "file",
#         "correction"
#     ]

#     for field in required_fields:

#         if field not in result:
#             raise ValueError(
#                 f"AI response missing field: {field}"
#             )

#     target_path = (
#         Path(repository) /
#         result["file"]
#     ).resolve()

#     repository_path = Path(
#         repository
#     ).resolve()

#     if repository_path not in target_path.parents:
#         raise ValueError(
#             "AI selected a file outside repository."
#         )

#     if not target_path.is_file():
#         raise ValueError(
#             "AI selected a file that does not exist: "
#             f"{result['file']}"
#         )

#     validate_target_file(
#         result["file"]
#     )

#     return result


# # ============================================================
# # FILE READER
# # ============================================================

# def read_file(
#     repo_path: str,
#     file_name: str
# ) -> str:

#     root = Path(repo_path).resolve()

#     file_path = (
#         root / file_name
#     ).resolve()

#     if root not in file_path.parents:
#         raise ValueError(
#             "Invalid file path."
#         )

#     if not file_path.is_file():
#         raise FileNotFoundError(
#             f"Target file does not exist: "
#             f"{file_name}"
#         )

#     return file_path.read_text(
#         encoding="utf-8"
#     )


# # ============================================================
# # TARGET FILE VALIDATION
# # ============================================================

# def validate_target_file(
#     file_name: str
# ):

#     path = Path(file_name)

#     filename = path.name.lower()

#     if filename.startswith("test_"):
#         raise ValueError(
#             "Agent is not allowed to modify test files."
#         )

#     if filename.endswith("_test.py"):
#         raise ValueError(
#             "Agent is not allowed to modify test files."
#         )

#     if filename == "conftest.py":
#         raise ValueError(
#             "Agent is not allowed to modify test configuration."
#         )


# # ============================================================
# # GENERATE INITIAL FIX
# # ============================================================

# def generate_fix(
#     issue: str,
#     repository: str,
#     analysis: dict,
#     target_file: str
# ) -> str:

#     current_code = read_file(
#         repository,
#         target_file
#     )

#     prompt = f"""
# You are an autonomous senior software engineer.

# Fix the actual defect in the repository.

# You have already received an analysis from another
# debugging stage.

# Do NOT use benchmark-specific knowledge.

# ============================================================
# ISSUE
# ============================================================

# {issue}

# ============================================================
# ROOT CAUSE
# ============================================================

# {analysis["root_cause"]}

# ============================================================
# REQUIRED CORRECTION
# ============================================================

# {analysis["correction"]}

# ============================================================
# TARGET FILE
# ============================================================

# {target_file}

# ============================================================
# CURRENT SOURCE CODE
# ============================================================

# {current_code}

# ============================================================
# RULES
# ============================================================

# 1. Fix the actual defect.
# 2. Preserve existing functionality.
# 3. Make the smallest correct change.
# 4. Do not modify tests.
# 5. Do not create new files.
# 6. Do not invent APIs.
# 7. Do not hardcode expected test outputs.
# 8. Do not write a solution for only one test case.
# 9. Generalize to valid inputs.
# 10. Preserve the public interface.
# 11. Return the COMPLETE corrected contents of the target file.
# 12. Return ONLY source code.
# 13. Do not use markdown fences.
# 14. Do not include explanations.

# Generate the corrected source code now.
# """

#     text = ask_ai(prompt)

#     text = clean_response(text)

#     if not text:
#         raise ValueError(
#             "AI generated an empty fix."
#         )

#     return text


# # ============================================================
# # UPDATE FILE
# # ============================================================

# def update_file(
#     repo_path: str,
#     file_name: str,
#     new_content: str
# ):

#     validate_target_file(
#         file_name
#     )

#     root = Path(repo_path).resolve()

#     file_path = (
#         root / file_name
#     ).resolve()

#     if root not in file_path.parents:
#         raise ValueError(
#             "Invalid file path."
#         )

#     if not file_path.is_file():
#         raise FileNotFoundError(
#             f"Target file does not exist: "
#             f"{file_name}"
#         )

#     file_path.write_text(
#         new_content.rstrip() + "\n",
#         encoding="utf-8"
#     )


# # ============================================================
# # CREATE BACKUP
# # ============================================================

# def create_backup(
#     repo_path: str,
#     target_file: str
# ) -> str:

#     root = Path(repo_path).resolve()

#     file_path = (
#         root / target_file
#     ).resolve()

#     if root not in file_path.parents:
#         raise ValueError(
#             "Invalid file path."
#         )

#     if not file_path.is_file():
#         raise FileNotFoundError(
#             f"Target file does not exist: "
#             f"{target_file}"
#         )

#     backup_path = file_path.with_suffix(
#         file_path.suffix + ".bak"
#     )

#     backup_path.write_text(
#         file_path.read_text(
#             encoding="utf-8"
#         ),
#         encoding="utf-8"
#     )

#     return str(backup_path)


# # ============================================================
# # RESTORE BACKUP
# # ============================================================

# def restore_backup(
#     repo_path: str,
#     target_file: str
# ):

#     root = Path(repo_path).resolve()

#     file_path = (
#         root / target_file
#     ).resolve()

#     backup_path = file_path.with_suffix(
#         file_path.suffix + ".bak"
#     )

#     if not backup_path.is_file():
#         raise FileNotFoundError(
#             f"Backup not found: {backup_path}"
#         )

#     file_path.write_text(
#         backup_path.read_text(
#             encoding="utf-8"
#         ),
#         encoding="utf-8"
#     )

#     backup_path.unlink()


# # ============================================================
# # RUN TESTS
# # ============================================================

# def run_tests(
#     repo_path: str
# ) -> dict:

#     print(
#         "\n========== RUNNING TESTS ==========\n"
#     )

#     try:

#         result = subprocess.run(
#             [
#                 "pytest",
#                 "-q"
#             ],
#             cwd=repo_path,
#             capture_output=True,
#             text=True,
#             timeout=120
#         )

#         output = (
#             result.stdout +
#             "\n" +
#             result.stderr
#         )

#         print(output)

#         return {
#             "passed": result.returncode == 0,
#             "output": output
#         }

#     except subprocess.TimeoutExpired:

#         return {
#             "passed": False,
#             "output": "Tests timed out."
#         }

#     except Exception as error:

#         return {
#             "passed": False,
#             "output": str(error)
#         }


# # ============================================================
# # GIT DIFF
# # ============================================================

# def get_git_diff(
#     repo_path: str
# ) -> str:

#     try:

#         result = subprocess.run(
#             [
#                 "git",
#                 "diff"
#             ],
#             cwd=repo_path,
#             capture_output=True,
#             text=True,
#             encoding="utf-8",
#             errors="replace",
#             timeout=30
#         )

#         if result.returncode != 0:

#             return (
#                 "Unable to generate git diff: "
#                 f"{result.stderr.strip()}"
#             )

#         return (
#             result.stdout or ""
#         ).strip()

#     except Exception as error:

#         return (
#             f"Unable to generate git diff: {error}"
#         )


# # ============================================================
# # SELF-CORRECTION
# # ============================================================

# def repair_fix(
#     issue: str,
#     repository: str,
#     analysis: dict,
#     target_file: str,
#     current_code: str,
#     test_output: str
# ) -> str:

#     prompt = f"""
# You are an autonomous software debugging agent.

# The previous AI-generated fix FAILED the tests.

# You must inspect the failure and produce a better fix.

# Do NOT use hardcoded benchmark-specific logic.

# ============================================================
# ORIGINAL ISSUE
# ============================================================

# {issue}

# ============================================================
# ROOT CAUSE
# ============================================================

# {analysis["root_cause"]}

# ============================================================
# PREVIOUS CORRECTION
# ============================================================

# {analysis["correction"]}

# ============================================================
# TARGET FILE
# ============================================================

# {target_file}

# ============================================================
# CURRENT CODE
# ============================================================

# {current_code}

# ============================================================
# TEST FAILURE
# ============================================================

# {test_output}

# ============================================================
# TASK
# ============================================================

# 1. Read the test failure carefully.
# 2. Determine why the previous fix failed.
# 3. Re-evaluate the implementation.
# 4. Correct the actual defect.
# 5. Preserve existing functionality.
# 6. Make the smallest necessary change.
# 7. Generalize to valid inputs.

# ============================================================
# STRICT RULES
# ============================================================

# - Do not modify tests.
# - Do not create new files.
# - Do not invent APIs.
# - Do not hardcode test outputs.
# - Do not create a solution for one test case.
# - Return the COMPLETE corrected contents of:

# {target_file}

# Return ONLY source code.

# Do not use markdown code fences.
# Do not include explanations.
# """

#     text = ask_ai(prompt)

#     text = clean_response(text)

#     if not text:
#         raise ValueError(
#             "AI generated an empty repair."
#         )

#     return text


# # ============================================================
# # LIST BENCHMARKS
# # ============================================================

# def get_benchmarks():

#     if not BENCHMARKS_DIR.exists():

#         raise FileNotFoundError(
#             f"Benchmarks directory not found: "
#             f"{BENCHMARKS_DIR}"
#         )

#     benchmarks = []

#     for directory in BENCHMARKS_DIR.iterdir():

#         if not directory.is_dir():
#             continue

#         if not directory.name.startswith("bug_"):
#             continue

#         issue_file = (
#             directory / "issue.txt"
#         )

#         repo_directory = (
#             directory / "repo"
#         )

#         if (
#             issue_file.is_file()
#             and repo_directory.is_dir()
#         ):

#             benchmarks.append(
#                 directory
#             )

#     benchmarks.sort(
#         key=lambda path: path.name
#     )

#     return benchmarks


# # ============================================================
# # SELECT BENCHMARK
# # ============================================================

# def select_benchmark():

#     benchmarks = get_benchmarks()

#     if not benchmarks:
#         raise RuntimeError(
#             "No valid benchmarks found."
#         )

#     print(
#         "\n========== AVAILABLE BUGS ==========\n"
#     )

#     for index, benchmark in enumerate(
#         benchmarks,
#         start=1
#     ):

#         print(
#             f"{index}. {benchmark.name}"
#         )

#     print()

#     while True:

#         choice = input(
#             "Select bug number: "
#         ).strip()

#         try:

#             number = int(choice)

#             if 1 <= number <= len(benchmarks):

#                 return benchmarks[
#                     number - 1
#                 ]

#         except ValueError:
#             pass

#         print(
#             "Invalid choice. Please try again."
#         )


# # ============================================================
# # RUN AGENT
# # ============================================================

# def run_agent(
#     benchmark: Path
# ):

#     repo_path = benchmark / "repo"

#     issue_path = benchmark / "issue.txt"

#     issue = issue_path.read_text(
#         encoding="utf-8"
#     )

#     print(
#         "\n========== READING REPOSITORY ==========\n"
#     )

#     repository = read_repository(
#         str(repo_path)
#     )

#     print(
#         "\n========== ANALYZING BUG ==========\n"
#     )

#     analysis = analyze_bug(
#         issue,
#         repository
#     )

#     print(
#         "\nRoot cause:",
#         analysis["root_cause"]
#     )

#     print(
#         "File:",
#         analysis["file"]
#     )

#     print(
#         "Correction:",
#         analysis["correction"]
#     )

#     target_file = analysis["file"]

#     validate_target_file(
#         target_file
#     )

#     current_code = read_file(
#         str(repo_path),
#         target_file
#     )

#     print(
#         "\n========== CREATING BACKUP ==========\n"
#     )

#     backup_path = create_backup(
#         str(repo_path),
#         target_file
#     )

#     print(
#         f"✓ Backup created: {backup_path}"
#     )

#     max_attempts = 3

#     test_result = None

#     for attempt in range(
#         1,
#         max_attempts + 1
#     ):

#         print(
#             f"\n========== ATTEMPT "
#             f"{attempt}/{max_attempts} ==========\n"
#         )

#         if attempt == 1:

#             print(
#                 "\n========== GENERATING INITIAL FIX ==========\n"
#             )

#             fixed_code = generate_fix(
#                 issue,
#                 repository,
#                 analysis,
#                 target_file
#             )

#         else:

#             print(
#                 "\n========== SELF-CORRECTION ==========\n"
#             )

#             fixed_code = repair_fix(
#                 issue,
#                 str(repo_path),
#                 analysis,
#                 target_file,
#                 current_code,
#                 test_result["output"]
#             )

#         fixed_code = clean_response(
#             fixed_code
#         )

#         print(
#             "\n========== PROPOSED CODE ==========\n"
#         )

#         print(fixed_code)

#         print(
#             "\n========== APPLYING FIX ==========\n"
#         )

#         update_file(
#             str(repo_path),
#             target_file,
#             fixed_code
#         )

#         current_code = fixed_code

#         print(
#             f"✓ Fix applied to {target_file}"
#         )

#         print(
#             "\n========== GENERATED DIFF ==========\n"
#         )

#         diff = get_git_diff(
#             str(repo_path)
#         )

#         print(
#             diff if diff else
#             "No git changes detected."
#         )

#         test_result = run_tests(
#             str(repo_path)
#         )

#         if test_result["passed"]:

#             print(
#                 "\n========================================"
#             )

#             print(
#                 "🎉 VERIFIED FIX"
#             )

#             print(
#                 f"✓ Tests passed on attempt {attempt}"
#             )

#             print(
#                 f"✓ Target file: {target_file}"
#             )

#             backup_file = Path(
#                 backup_path
#             )

#             if backup_file.exists():

#                 backup_file.unlink()

#                 print(
#                     "✓ Backup removed"
#                 )

#             print(
#                 "========================================"
#             )

#             return True

#         print(
#             f"\n❌ Attempt {attempt} failed."
#         )

#         if attempt < max_attempts:

#             current_code = read_file(
#                 str(repo_path),
#                 target_file
#             )

#     print(
#         "\n========================================"
#     )

#     print(
#         "❌ FIX NOT VERIFIED"
#     )

#     print(
#         "Maximum attempts reached."
#     )

#     print(
#         "\n========== ROLLING BACK ==========\n"
#     )

#     try:

#         restore_backup(
#             str(repo_path),
#             target_file
#         )

#         print(
#             f"✓ Original code restored for "
#             f"{target_file}"
#         )

#     except Exception as error:

#         print(
#             f"❌ Rollback failed: {error}"
#         )

#     print(
#         "========================================"
#     )

#     return False


# # ============================================================
# # MAIN
# # ============================================================

# def main():

#     print(
#         "\n========================================"
#     )

#     print(
#         "🤖 AUTONOMOUS BUG FIX AGENT"
#     )

#     print(
#         "========================================"
#     )

#     benchmark = select_benchmark()

#     print(
#         f"\nSelected benchmark: {benchmark.name}"
#     )

#     print(
#         f"Repository: {benchmark / 'repo'}"
#     )

#     print(
#         f"Issue: {benchmark / 'issue.txt'}"
#     )

#     try:

#         run_agent(
#             benchmark
#         )

#     except Exception as error:

#         print(
#             "\n========================================"
#         )

#         print(
#             "❌ AGENT ERROR"
#         )

#         print(
#             "========================================"
#         )

#         print(error)


# # ============================================================
# # ENTRY POINT
# # ============================================================

# if __name__ == "__main__":
#     main()



import os
import re
import json
import time
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from backend.patcher import (
    validate_target_file,
    create_backup,
    apply_fix,
    restore_backup,
    remove_backup,
    get_diff,
    validate_python_syntax,
)


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = None


def get_ai_client():
    """
    Lazily create the Gemini client.

    This prevents importing backend.agent from failing when
    the API key is unavailable. The key is required only when
    an actual AI request is made.
    """
    global client

    if client is not None:
        return client

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. "
            "Add GEMINI_API_KEY to backend/.env before "
            "running an AI-powered bug-fix."
        )

    client = genai.Client(
        api_key=api_key
    )

    return client

MODEL = os.getenv(
    "MODEL_NAME",
    "gemini-2.5-flash-lite"
)

MAX_AI_RETRIES = int(
    os.getenv("MAX_AI_RETRIES", "3")
)

AI_RETRY_DELAY = float(
    os.getenv("AI_RETRY_DELAY", "5")
)


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

BENCHMARKS_DIR = BASE_DIR / "benchmarks"


# ============================================================
# AI REQUEST LAYER
# ============================================================

def ask_ai(prompt: str) -> str:
    """
    Centralized AI request layer.

    All AI communication goes through this function.
    """

    last_error = None

    for attempt in range(
        1,
        MAX_AI_RETRIES + 1
    ):

        try:

            print(
                f"\n🤖 AI request "
                f"({attempt}/{MAX_AI_RETRIES})..."
            )

            response = get_ai_client().models.generate_content(
                model=MODEL,
                contents=prompt
            )

            if not response:
                raise RuntimeError(
                    "AI returned no response."
                )

            if not response.text:
                raise RuntimeError(
                    "AI returned an empty response."
                )

            return response.text.strip()

        except Exception as error:

            last_error = error

            print(
                f"\n⚠ AI request failed: {error}"
            )

            if attempt < MAX_AI_RETRIES:

                wait_time = (
                    AI_RETRY_DELAY * attempt
                )

                print(
                    f"⏳ Retrying in "
                    f"{wait_time:.1f} seconds..."
                )

                time.sleep(wait_time)

    raise RuntimeError(
        f"AI request failed after "
        f"{MAX_AI_RETRIES} attempts: "
        f"{last_error}"
    )


# ============================================================
# CLEAN AI RESPONSE
# ============================================================

def clean_response(content: str) -> str:
    """
    Remove markdown code fences and surrounding whitespace.
    """

    if not content:
        return ""

    content = content.strip()

    content = re.sub(
        r"^```(?:python|json|text)?\s*",
        "",
        content,
        flags=re.IGNORECASE
    )

    content = re.sub(
        r"\s*```$",
        "",
        content
    )

    return content.strip()


# ============================================================
# READ REPOSITORY
# ============================================================

def read_repository(
    repo_path: str
) -> str:
    """
    Read supported source files from a repository.

    Tests are included so the AI can understand expected
    behavior, but the agent will never intentionally modify
    test files.
    """

    root = Path(repo_path).resolve()

    if not root.is_dir():
        raise FileNotFoundError(
            f"Repository not found: {repo_path}"
        )

    ignored_directories = {
        ".git",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        ".venv",
        "venv",
        "dist",
        "build",
    }

    supported_extensions = {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".cpp",
        ".c",
        ".h",
        ".cs",
        ".go",
        ".rs",
        ".rb",
        ".php",
        ".sql",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".md",
        ".txt",
    }

    files = []

    for path in root.rglob("*"):

        if not path.is_file():
            continue

        if any(
            part in ignored_directories
            for part in path.parts
        ):
            continue

        if path.suffix.lower() not in supported_extensions:
            continue

        try:

            content = path.read_text(
                encoding="utf-8"
            )

        except (
            UnicodeDecodeError,
            OSError
        ):

            continue

        relative_path = path.relative_to(root)

        files.append(
            f"\n===== FILE: {relative_path} =====\n"
            f"{content}"
        )

    return "\n".join(files)


# ============================================================
# BUG ANALYSIS
# ============================================================
def analyze_bug(
    issue: str,
    repository: str,
    repository_contents: str
) -> dict:
    """
    Analyze the reported bug and identify the exact source file.

    repository:
        Actual repository filesystem path.

    repository_contents:
        Text snapshot of repository files supplied to the AI.
    """

    prompt = f"""
You are an autonomous senior software debugging agent.

Investigate the repository and determine the actual root
cause of the reported issue.

Do NOT rely on benchmark names.
Do NOT assume a known bug pattern.

============================================================
ISSUE
============================================================

{issue}

============================================================
REPOSITORY CONTENTS
============================================================

{repository_contents}

============================================================
TASK
============================================================

1. Understand the reported issue.
2. Inspect the relevant source files.
3. Inspect tests when useful.
4. Determine expected behavior.
5. Determine actual behavior.
6. Identify the exact root cause.
7. Identify the exact source file that must be modified.
8. Describe the smallest correct correction.

============================================================
STRICT RULES
============================================================

- Do not modify tests.
- Do not select a test file.
- Do not invent files.
- Select only a file that exists.
- Do not hardcode benchmark-specific solutions.
- Do not assume a particular filename.
- Do not assume a particular bug pattern.
- Generalize to valid inputs.
- Preserve existing APIs.
- Keep the correction minimal.

Return ONLY valid JSON.

Required format:

{{
    "root_cause": "actual defect",
    "file": "relative/path/to/source/file",
    "correction": "precise correction"
}}
"""

    text = ask_ai(prompt)
    text = clean_response(text)

    try:
        result = json.loads(text)

    except json.JSONDecodeError:

        match = re.search(
            r"\{.*\}",
            text,
            re.DOTALL
        )

        if not match:
            raise ValueError(
                "AI did not return valid JSON."
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
                f"AI response missing field: {field}"
            )

    repository_path = Path(
        repository
    ).resolve()

    target_path = (
        repository_path /
        result["file"]
    ).resolve()

    # Prevent path traversal.
    if repository_path not in target_path.parents:
        raise ValueError(
            "AI selected a file outside repository."
        )

    if not target_path.is_file():
        raise ValueError(
            "AI selected a file that does not exist: "
            f"{result['file']}"
        )

    validate_target_file(
        str(repository_path),
        result["file"]
    )

    return result

# ============================================================
# FILE READER
# ============================================================

def read_file(
    repo_path: str,
    file_name: str
) -> str:
    """
    Read a specific repository file.
    """

    root = Path(repo_path).resolve()

    file_path = (
        root / file_name
    ).resolve()

    if root not in file_path.parents:

        raise ValueError(
            "Invalid file path."
        )

    if not file_path.is_file():

        raise FileNotFoundError(
            f"Target file does not exist: "
            f"{file_name}"
        )

    return file_path.read_text(
        encoding="utf-8"
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
    """
    Generate the initial source-code fix.
    """

    current_code = read_file(
        repository,
        target_file
    )

    prompt = f"""
You are an autonomous senior software engineer.

Fix the actual defect in the repository.

You have already received an analysis from another
debugging stage.

Do NOT use benchmark-specific knowledge.

============================================================
ISSUE
============================================================

{issue}

============================================================
ROOT CAUSE
============================================================

{analysis["root_cause"]}

============================================================
REQUIRED CORRECTION
============================================================

{analysis["correction"]}

============================================================
TARGET FILE
============================================================

{target_file}

============================================================
CURRENT SOURCE CODE
============================================================

{current_code}

============================================================
RULES
============================================================

1. Fix the actual defect.
2. Preserve existing functionality.
3. Make the smallest correct change.
4. Do not modify tests.
5. Do not create new files.
6. Do not invent APIs.
7. Do not hardcode expected test outputs.
8. Do not solve only one test case.
9. Generalize to valid inputs.
10. Preserve the public interface.
11. Return COMPLETE corrected contents.
12. Return ONLY source code.
13. Do not use markdown fences.
14. Do not include explanations.

Generate the corrected source code now.
"""

    text = ask_ai(prompt)

    text = clean_response(text)

    if not text:

        raise ValueError(
            "AI generated an empty fix."
        )

    return text


# ============================================================
# RUN TESTS
# ============================================================

def run_tests(
    repo_path: str
) -> dict:
    """
    Run pytest for the repository.
    """

    print(
        "\n========== RUNNING TESTS ==========\n"
    )

    try:

        result = subprocess.run(
            [
                "pytest",
                "-q"
            ],
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
            "output": output,
        }

    except subprocess.TimeoutExpired:

        return {
            "passed": False,
            "output": "Tests timed out.",
        }

    except Exception as error:

        return {
            "passed": False,
            "output": str(error),
        }

# ============================================================
# FAILURE CLASSIFICATION
# ============================================================

def classify_failure(test_output: str) -> dict:
    """
    Analyze pytest output and classify the failure.

    This is deterministic and does not require an AI request.
    """

    if not test_output:
        return {
            "type": "unknown",
            "severity": "high",
            "reason": "No test output was produced."
        }

    output = test_output.lower()

    # --------------------------------------------------------
    # SYNTAX ERROR
    # --------------------------------------------------------

    if (
        "syntaxerror" in output
        or "invalid syntax" in output
    ):
        return {
            "type": "syntax_error",
            "severity": "critical",
            "reason": "The generated source code contains invalid Python syntax."
        }

    # --------------------------------------------------------
    # IMPORT ERROR
    # --------------------------------------------------------

    if (
        "modulenotfounderror" in output
        or "importerror" in output
    ):
        return {
            "type": "import_error",
            "severity": "high",
            "reason": "The patched code contains an import or module dependency problem."
        }

    # --------------------------------------------------------
    # NAME ERROR
    # --------------------------------------------------------

    if "nameerror" in output:
        return {
            "type": "name_error",
            "severity": "high",
            "reason": "The patch references an undefined variable, function, or name."
        }

    # --------------------------------------------------------
    # TYPE ERROR
    # --------------------------------------------------------

    if "typeerror" in output:
        return {
            "type": "type_error",
            "severity": "high",
            "reason": "The patch caused an incompatible type operation."
        }

    # --------------------------------------------------------
    # ATTRIBUTE ERROR
    # --------------------------------------------------------

    if "attributeerror" in output:
        return {
            "type": "attribute_error",
            "severity": "high",
            "reason": "The patch accessed an invalid or missing attribute."
        }

    # --------------------------------------------------------
    # ASSERTION / TEST FAILURE
    # --------------------------------------------------------

    if (
        "assert " in output
        or "failed" in output
        or "assertionerror" in output
    ):
        return {
            "type": "test_failure",
            "severity": "medium",
            "reason": "The patched implementation does not satisfy the expected behavior."
        }

    # --------------------------------------------------------
    # TIMEOUT
    # --------------------------------------------------------

    if (
        "timed out" in output
        or "timeout" in output
    ):
        return {
            "type": "timeout",
            "severity": "critical",
            "reason": "The test execution exceeded the allowed time."
        }

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    return {
        "type": "unknown",
        "severity": "high",
        "reason": "The failure could not be classified automatically."
    }
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
    """
    Generate a better fix after a failed test attempt.
    """

    prompt = f"""
You are an autonomous software debugging agent.

The previous AI-generated fix FAILED the tests.

Inspect the failure and produce a better fix.

Do NOT use hardcoded benchmark-specific logic.

============================================================
ORIGINAL ISSUE
============================================================

{issue}

============================================================
ROOT CAUSE
============================================================

{analysis["root_cause"]}

============================================================
PREVIOUS CORRECTION
============================================================

{analysis["correction"]}

============================================================
TARGET FILE
============================================================

{target_file}

============================================================
CURRENT CODE
============================================================

{current_code}

============================================================
TEST FAILURE
============================================================

{test_output}

============================================================
TASK
============================================================

1. Read the test failure carefully.
2. Determine why the previous fix failed.
3. Re-evaluate the implementation.
4. Correct the actual defect.
5. Preserve existing functionality.
6. Make the smallest necessary change.
7. Generalize to valid inputs.

============================================================
STRICT RULES
============================================================

- Do not modify tests.
- Do not create new files.
- Do not invent APIs.
- Do not hardcode test outputs.
- Do not create a one-test-case solution.
- Return COMPLETE corrected contents of:

{target_file}

Return ONLY source code.

Do not use markdown code fences.
Do not include explanations.
"""

    text = ask_ai(prompt)

    text = clean_response(text)

    if not text:

        raise ValueError(
            "AI generated an empty repair."
        )

    return text


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

        issue_file = (
            directory / "issue.txt"
        )

        repo_directory = (
            directory / "repo"
        )

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
# RUN AGENT
# ============================================================
# ============================================================
# RUN AGENT
# ============================================================
def verify_initial_bug(repo_path: str) -> dict:
    """
    Run the repository tests before attempting any modification.

    This establishes that the benchmark actually contains
    a failing test before the autonomous repair begins.
    """

    print(
        "\n========== VERIFYING INITIAL BUG ==========\n"
    )

    result = run_tests(repo_path)

    if result["passed"]:
        print(
            "⚠ WARNING: Initial repository tests passed."
        )
        print(
            "The benchmark may not contain an active failing bug."
        )
    else:
        print(
            "✓ Initial tests failed as expected."
        )

    return result

# ============================================================
# PATCH SAFETY GATE
# ============================================================

def validate_patch_safety(
    repo_path: str,
    target_file: str,
    original_code: str,
    proposed_code: str
) -> dict:
    """
    Validate an AI-generated patch before it is applied.

    The safety gate prevents:
    - test modification
    - changes outside the target file
    - excessively large rewrites
    - empty patches
    - suspicious source destruction
    """

    root = Path(repo_path).resolve()

    target_path = (
        root / target_file
    ).resolve()

    # --------------------------------------------------------
    # TARGET PATH VALIDATION
    # --------------------------------------------------------

    if root not in target_path.parents:
        return {
            "safe": False,
            "reason": "Target file is outside repository."
        }

    if not target_path.is_file():
        return {
            "safe": False,
            "reason": "Target file does not exist."
        }

    # --------------------------------------------------------
    # TEST FILE PROTECTION
    # --------------------------------------------------------

    target_name = target_path.name.lower()

    if (
        target_name.startswith("test_")
        or target_name.endswith("_test.py")
        or "test" in target_name
    ):
        return {
            "safe": False,
            "reason": "Agent is not allowed to modify test files."
        }

    # --------------------------------------------------------
    # EMPTY PATCH CHECK
    # --------------------------------------------------------

    if original_code == proposed_code:
        return {
            "safe": False,
            "reason": "Generated patch contains no changes."
        }

    # --------------------------------------------------------
    # BASIC SIZE CHECK
    # --------------------------------------------------------

    original_lines = original_code.splitlines()
    proposed_lines = proposed_code.splitlines()

    original_count = len(original_lines)
    proposed_count = len(proposed_lines)

    changed_lines = 0

    max_lines = max(
        original_count,
        proposed_count
    )

    for index in range(max_lines):

        old_line = (
            original_lines[index]
            if index < original_count
            else None
        )

        new_line = (
            proposed_lines[index]
            if index < proposed_count
            else None
        )

        if old_line != new_line:
            changed_lines += 1

    # --------------------------------------------------------
    # PREVENT MASSIVE REWRITES
    # --------------------------------------------------------

    if (
        original_count > 0
        and changed_lines > max(
            20,
            int(original_count * 0.70)
        )
    ):
        return {
            "safe": False,
            "reason": (
                "Generated patch is excessively large "
                "relative to the original file."
            )
        }

    # --------------------------------------------------------
    # BASIC DESTRUCTIVE CHANGE CHECK
    # --------------------------------------------------------

    removed_lines = max(
        0,
        original_count - proposed_count
    )

    if (
        original_count >= 10
        and removed_lines > original_count * 0.5
    ):
        return {
            "safe": False,
            "reason": (
                "Generated patch removes too much "
                "existing source code."
            )
        }

    # --------------------------------------------------------
    # RETURN SAFETY RESULT
    # --------------------------------------------------------

    return {
        "safe": True,
        "reason": "Patch passed safety validation.",
        "original_lines": original_count,
        "proposed_lines": proposed_count,
        "changed_lines": changed_lines
    }

def run_agent(
    benchmark: Path
):
    """
    Execute the complete autonomous bug-fixing workflow.

    Workflow:
        1. Read issue
        2. Read repository
        3. Analyze bug using AI
        4. Create backup
        5. Generate fix
        6. Validate generated code
        7. Apply fix
        8. Validate patched file
        9. Generate git diff
        10. Run tests
        11. Classify failures
        12. Self-correct when necessary
        13. Roll back if all attempts fail
    """

    repo_path = benchmark / "repo"
    issue_path = benchmark / "issue.txt"

    # ========================================================
    # READ ISSUE
    # ========================================================

    issue = issue_path.read_text(
        encoding="utf-8"
    )

 

    initial_test_result = verify_initial_bug(
        str(repo_path)
    )

    # ========================================================
    # READ REPOSITORY
    # ========================================================

    print(
        "\n========== READING REPOSITORY ==========\n"
    )

    repository = read_repository(
        str(repo_path)
    )

    # ========================================================
    # ANALYZE BUG
    # ========================================================

    print(
        "\n========== ANALYZING BUG ==========\n"
    )

    analysis = analyze_bug(
    issue,
    str(repo_path),
    repository
)
    print(
        "\nRoot cause:",
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

    target_file = analysis["file"]

    # ========================================================
    # VALIDATE TARGET
    # ========================================================

    validate_target_file(
        str(repo_path),
        target_file
    )

    current_code = read_file(
        str(repo_path),
        target_file
    )

    # ========================================================
    # CREATE BACKUP
    # ========================================================

    print(
        "\n========== CREATING BACKUP ==========\n"
    )

    backup_path = create_backup(
        str(repo_path),
        target_file
    )

    print(
        f"✓ Backup created: {backup_path}"
    )

    # ========================================================
    # ATTEMPT LOOP
    # ========================================================

    max_attempts = 3
    test_result = None

    for attempt in range(
        1,
        max_attempts + 1
    ):

        print(
            "\n" + "=" * 50
        )

        print(
            f"ATTEMPT {attempt}/{max_attempts}"
        )

        print(
            "=" * 50
        )

        # ====================================================
        # GENERATE FIX
        # ====================================================

        try:

            if attempt == 1:

                print(
                    "\n========== GENERATING INITIAL FIX ==========\n"
                )

                fixed_code = generate_fix(
                    issue,
                    str(repo_path),
                    analysis,
                    target_file
                )

            else:

                print(
                    "\n========== SELF-CORRECTION ==========\n"
                )

                fixed_code = repair_fix(
                    issue,
                    str(repo_path),
                    analysis,
                    target_file,
                    current_code,
                    test_result["output"]
                )

            fixed_code = clean_response(
                fixed_code
            )

        except Exception as error:

            print(
                f"\n✗ AI fix generation failed: {error}"
            )

            test_result = {
                "passed": False,
                "output": (
                    "AI fix generation failed:\n"
                    + str(error)
                )
            }

            if attempt < max_attempts:
                continue

            break

        # ====================================================
        # SHOW PROPOSED CODE
        # ====================================================

        print(
            "\n========== PROPOSED CODE ==========\n"
        )

        print(
            fixed_code
        )

        # ====================================================
        # VALIDATE GENERATED CODE
        # ====================================================

        print(
            "\n========== VALIDATING GENERATED FIX ==========\n"
        )

        try:

            validate_python_syntax(
                fixed_code
            )

            print(
                "✓ Generated fix passed syntax validation."
            )

        except Exception as error:

            print(
                f"✗ Generated fix failed syntax validation: "
                f"{error}"
            )

            test_result = {
                "passed": False,
                "output": (
                    "Generated fix failed syntax validation:\n"
                    + str(error)
                )
            }

            if attempt < max_attempts:
                continue

            break

        # ====================================================
        # APPLY FIX
        # ====================================================

        print(
            "\n========== APPLYING FIX ==========\n"
        )

        try:

            apply_fix(
                str(repo_path),
                target_file,
                fixed_code
            )

            print(
                f"✓ Fix applied to {target_file}"
            )

        except Exception as error:

            print(
                f"✗ Failed to apply fix: {error}"
            )

            test_result = {
                "passed": False,
                "output": (
                    "Failed to apply generated fix:\n"
                    + str(error)
                )
            }

            if attempt < max_attempts:
                continue

            break

        # ====================================================
        # READ ACTUAL PATCHED FILE
        # ====================================================

        try:

            current_code = read_file(
                str(repo_path),
                target_file
            )

        except Exception as error:

            print(
                f"✗ Could not read patched file: {error}"
            )

            test_result = {
                "passed": False,
                "output": (
                    "Could not read patched file:\n"
                    + str(error)
                )
            }

            if attempt < max_attempts:
                continue

            break 
                # ====================================================
        # PATCH SAFETY GATE
        # ====================================================

        print(
            "\n========== PATCH SAFETY GATE ==========\n"
        )

        safety_result = validate_patch_safety(
            str(repo_path),
            target_file,
            current_code,
            fixed_code
        )

        print(
            "Safety status : "
            + (
                "SAFE"
                if safety_result["safe"]
                else "REJECTED"
            )
        )

        print(
            f"Safety reason : "
            f"{safety_result['reason']}"
        )

        if "changed_lines" in safety_result:

            print(
                f"Changed lines : "
                f"{safety_result['changed_lines']}"
            )

        # ----------------------------------------------------
        # REJECT UNSAFE PATCH
        # ----------------------------------------------------

        if not safety_result["safe"]:

            print(
                "\n⚠ Patch rejected by safety gate."
            )

            test_result = {
                "passed": False,
                "output": (
                    "Patch rejected by safety gate:\n"
                    + safety_result["reason"]
                )
            }

            if attempt < max_attempts:
                continue

            break

        print(
            "✓ Patch passed safety gate."
        )

        # ====================================================
        # VALIDATE PATCHED FILE
        # ====================================================

        print(
            "\n========== VALIDATING TARGET FILE ==========\n"
        )

        try:

            validate_python_syntax(
                current_code
            )

            print(
                "✓ Patched file passed syntax validation."
            )

        except Exception as error:

            print(
                f"✗ Patched file failed syntax validation: "
                f"{error}"
            )

            print(
                "\n========== AUTOMATIC ROLLBACK ==========\n"
            )

            try:

                restore_backup(
                    str(repo_path),
                    target_file
                )

                print(
                    "✓ Invalid patch automatically rolled back."
                )

            except Exception as rollback_error:

                print(
                    f"✗ Rollback failed: "
                    f"{rollback_error}"
                )

            current_code = read_file(
                str(repo_path),
                target_file
            )

            test_result = {
                "passed": False,
                "output": (
                    "Patched file failed syntax validation:\n"
                    + str(error)
                )
            }

            if attempt < max_attempts:
                continue

            break

        # ====================================================
        # GENERATED DIFF
        # ====================================================

        print(
            "\n========== GENERATED DIFF ==========\n"
        )

        try:

            diff = get_diff(
                str(repo_path)
            )

            print(
                diff
                if diff
                else
                "No git changes detected."
            )

        except Exception as error:

            print(
                f"⚠ Could not generate diff: {error}"
            )

        # ====================================================
        # RUN TESTS
        # ====================================================

        test_result = run_tests(
            str(repo_path)
        )

        # ====================================================
        # SUCCESS
        # ====================================================

        if test_result["passed"]:

            print(
                "\n" + "=" * 50
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
                "=" * 50
            )

            try:

                remove_backup(
                    str(repo_path),
                    target_file
                )

                print(
                    "✓ Backup removed"
                )

            except Exception as error:

                print(
                    f"⚠ Could not remove backup: {error}"
                )

            return True

        # ====================================================
        # FAILURE ANALYSIS
        # ====================================================

        print(
            f"\n❌ Attempt {attempt} failed."
        )

        failure = classify_failure(
            test_result["output"]
        )

        print(
            "\n========== FAILURE ANALYSIS ==========\n"
        )

        print(
            f"Failure type : {failure['type']}"
        )

        print(
            f"Severity     : {failure['severity']}"
        )

        print(
            f"Reason       : {failure['reason']}"
        )

        # ====================================================
        # PREPARE NEXT ATTEMPT
        # ====================================================

        if attempt < max_attempts:

            print(
                "\n↻ Preparing intelligent self-correction..."
            )

            try:

                current_code = read_file(
                    str(repo_path),
                    target_file
                )

            except Exception:

                current_code = fixed_code

    # ========================================================
    # ALL ATTEMPTS FAILED
    # ========================================================

    print(
        "\n" + "=" * 50
    )

    print(
        "❌ FIX NOT VERIFIED"
    )

    print(
        "Maximum attempts reached."
    )

    print(
        "=" * 50
    )

    # ========================================================
    # ROLLBACK
    # ========================================================

    print(
        "\n========== ROLLING BACK ==========\n"
    )

    try:

        restore_backup(
            str(repo_path),
            target_file
        )

        print(
            f"✓ Original code restored for "
            f"{target_file}"
        )

    except Exception as error:

        print(
            f"❌ Rollback failed: {error}"
        )

    print(
        "\n========================================"
    )

    return False

# ============================================================
# MAIN
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

    benchmark = select_benchmark()

    print(
        f"\nSelected benchmark: {benchmark.name}"
    )

    print(
        f"Repository: {benchmark / 'repo'}"
    )

    print(
        f"Issue: {benchmark / 'issue.txt'}"
    )

    try:

        success = run_agent(
            benchmark
        )

        if success:

            print(
                "\n✅ Agent completed successfully."
            )

        else:

            print(
                "\n❌ Agent could not verify the fix."
            )

    except Exception as error:

        print(
            "\n========================================"
        )

        print(
            "❌ AGENT ERROR"
        )

        print(
            "========================================"
        )

        print(error)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()