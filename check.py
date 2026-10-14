"""CS 1430 Baby Shark checker.

Run this file to check your work:   python check.py

Fix the FIRST line that says FAIL, save, and run this file again.
You do not need to read or change anything in this file.
"""

import ast
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = HERE / "main.py"
TEMPLATE_URL = "github.com/CS1430/baby-shark-lab/blob/main/main.py"

DOO = "doo-doo-doo-do-do-do-do"
REPEAT_VALUE = 3

EXPECTED = []
for _who in ("Baby", "Mommy", "Daddy"):
    for _ in range(REPEAT_VALUE):
        EXPECTED += [f"{_who} Shark,", DOO]
    EXPECTED.append(f"{_who} Shark!")


# ---------------------------------------------------------------- output

def _use_color():
    if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
        return False
    if os.name == "nt":
        os.system("")  # turns on color codes in the Windows terminal
    return True


COLOR = _use_color()


def _paint(text, code):
    return f"\033[{code}m{text}\033[0m" if COLOR else text


LABELS = {
    "PASS": _paint("[PASS]", "32"),
    "FAIL": _paint("[FAIL]", "31"),
    "SKIP": _paint("[ -- ]", "90"),
}


class Report:
    def __init__(self):
        self.first_fail_shown = False
        self.failed = False

    def heading(self, text):
        print()
        print(_paint(text, "1"))

    def line(self, status, text, hint=""):
        print(f"  {LABELS[status]} {text}")
        if status == "FAIL":
            self.failed = True
            if hint and not self.first_fail_shown:
                for hint_line in hint.strip().splitlines():
                    print(_paint(f"         > {hint_line}", "33"))
            self.first_fail_shown = True

    def skip(self, *texts):
        for text in texts:
            self.line("SKIP", text)


L_NAME = "Your name is in the header"
L_SYNTAX = "main.py has no syntax errors"
L_RUNS = "main.py runs"
L_SONG = f"Prints all {len(EXPECTED)} lines of the song, exactly"
L_REPEAT = f"REPEAT = {REPEAT_VALUE} is still at the top"
L_DEF = "One verse-maker: a def (besides main) with one parameter"
L_PARAM = "The verse-maker uses its parameter"
L_LOOP = "The verse-maker repeats with  for ... in range(REPEAT)"
L_DOO = "The doo-doo line is typed only once"
L_MAIN = "main() makes three calls to the verse-maker, and nothing else"
L_GUARD = "Everything runs from main(), through  if __name__ == \"__main__\":"

AFTER_SYNTAX = [L_RUNS, L_SONG, L_REPEAT, L_DEF, L_PARAM, L_LOOP, L_DOO, L_MAIN, L_GUARD]


# ---------------------------------------------------------------- helpers

def run_git(*args, timeout=20):
    """Run a git command in this folder. Returns (ok, output)."""
    try:
        result = subprocess.run(
            ["git", *args], cwd=HERE, capture_output=True, text=True,
            timeout=timeout, encoding="utf-8", errors="replace",
        )
    except (OSError, subprocess.TimeoutExpired) as err:
        return False, str(err)
    return result.returncode == 0, (result.stdout + result.stderr).strip()


def run_main():
    """Run main.py. Returns (returncode, stdout, stderr)."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    try:
        result = subprocess.run(
            [sys.executable, str(MAIN)], cwd=HERE, input="",
            capture_output=True, text=True, timeout=10, env=env,
            encoding="utf-8", errors="replace",
        )
    except subprocess.TimeoutExpired:
        return None, "", "timeout"
    return result.returncode, result.stdout, result.stderr


def explain_crash(stderr):
    last = stderr.strip().splitlines()[-1] if stderr.strip() else "(no message)"
    if last.startswith("NameError"):
        return ("main.py crashed on a name Python doesn't know.\n"
                "Check the spelling and capitals of every name you used,\n"
                "and check that each def comes before the line that runs it.\n"
                f"Python said: {last}")
    if last.startswith("TypeError") and "argument" in last:
        return ("The number of values in a call doesn't match the number of\n"
                "parameters in the def. Compare the two lines.\n"
                f"Python said: {last}")
    if last.startswith("EOFError"):
        return "This program doesn't ask the user for anything. Take out input()."
    return f"main.py crashed. The last line of the error was:\n{last}"


def module_docstring(tree):
    if (tree.body and isinstance(tree.body[0], ast.Expr)
            and isinstance(tree.body[0].value, ast.Constant)
            and isinstance(tree.body[0].value.value, str)):
        return tree.body[0]
    return None


def is_name(node, name):
    return isinstance(node, ast.Name) and node.id == name


def is_call_to(node, name):
    return isinstance(node, ast.Call) and is_name(node.func, name)


def is_main_guard(stmt):
    """True for:  if __name__ == "__main__":  main()"""
    if not isinstance(stmt, ast.If) or stmt.orelse:
        return False
    test = stmt.test
    if not (isinstance(test, ast.Compare) and len(test.ops) == 1
            and isinstance(test.ops[0], ast.Eq)):
        return False
    sides = [test.left, test.comparators[0]]
    has_name = any(is_name(s, "__name__") for s in sides)
    has_main = any(isinstance(s, ast.Constant) and s.value == "__main__" for s in sides)
    body_ok = (len(stmt.body) == 1 and isinstance(stmt.body[0], ast.Expr)
               and is_call_to(stmt.body[0].value, "main") and not stmt.body[0].value.args)
    return has_name and has_main and body_ok


def body_without_docstring(func):
    body = func.body
    if (body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)):
        return body[1:]
    return body


def is_range_repeat(node):
    """range(REPEAT) or range(0, REPEAT)."""
    if not is_call_to(node, "range") or node.keywords:
        return False
    args = node.args
    if len(args) == 1:
        return is_name(args[0], "REPEAT")
    if len(args) == 2:
        return (isinstance(args[0], ast.Constant) and args[0].value == 0
                and is_name(args[1], "REPEAT"))
    return False


# ---------------------------------------------------------------- code checks

def check_name(report, tree):
    doc = module_docstring(tree)
    if doc is None:
        report.line("FAIL", L_NAME,
                    "The header comment at the top of main.py is missing.\n"
                    f"Copy it back from the class template:\n{TEMPLATE_URL}")
    elif "your name" in doc.value.value.lower():
        report.line("FAIL", L_NAME,
                    "Line 2 of main.py still says \"your name\". Type your own name there.")
    else:
        report.line("PASS", L_NAME)


def check_song(report):
    code, out, err = run_main()
    if code is None:
        report.line("FAIL", L_RUNS,
                    "main.py was still running after 10 seconds.\n"
                    "Look for a loop that never ends.")
        report.skip(L_SONG)
        return
    if code != 0:
        report.line("FAIL", L_RUNS, explain_crash(err))
        report.skip(L_SONG)
        return
    report.line("PASS", L_RUNS)

    got = [ln.rstrip() for ln in out.replace("\r\n", "\n").split("\n")]
    while got and not got[-1]:
        got.pop()
    if got == EXPECTED:
        report.line("PASS", L_SONG)
        return
    for i in range(max(len(got), len(EXPECTED))):
        want = EXPECTED[i] if i < len(EXPECTED) else "(nothing, the song is over)"
        have = got[i] if i < len(got) else "(nothing)"
        if want != have:
            report.line("FAIL", L_SONG,
                        f"Line {i + 1} of the output is different.\n"
                        f"  should be: {want}\n"
                        f"  yours is:  {have}\n"
                        "Spaces, commas, and capitals all count.")
            return


def check_repeat(report, tree):
    for stmt in tree.body:
        if (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                and is_name(stmt.targets[0], "REPEAT")):
            if isinstance(stmt.value, ast.Constant) and stmt.value.value == REPEAT_VALUE:
                report.line("PASS", L_REPEAT)
            else:
                report.line("FAIL", L_REPEAT,
                            f"Leave the constant at the top as  REPEAT = {REPEAT_VALUE}")
            return
    report.line("FAIL", L_REPEAT,
                f"The line  REPEAT = {REPEAT_VALUE}  is missing from the top of the file.\n"
                "Put it back under the CONSTANTS heading.")


def check_structure(report, tree):
    """Returns nothing; reports L_DEF through L_MAIN."""
    helpers = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name != "main"]
    main_node = next((n for n in tree.body
                      if isinstance(n, ast.FunctionDef) and n.name == "main"), None)

    # ---- one def with one parameter
    verse = None
    if not helpers:
        report.line("FAIL", L_DEF,
                    "Right now main() spells out every verse by hand. The three verses\n"
                    "are the same except for one word. Write a def that prints ONE verse,\n"
                    "with a parameter for the word that changes. Put it above main().")
    elif len(helpers) > 1:
        names = ", ".join(h.name for h in helpers)
        report.line("FAIL", L_DEF,
                    f"Found {len(helpers)} defs besides main(): {names}.\n"
                    "This lab uses just one, the one that prints a verse.")
    else:
        verse = helpers[0]
        a = verse.args
        params = a.posonlyargs + a.args
        if len(params) != 1 or a.vararg or a.kwarg or a.kwonlyargs:
            report.line("FAIL", L_DEF,
                        f"def {verse.name}(...) on line {verse.lineno} should have exactly one\n"
                        "parameter: a name inside the parentheses for the word that changes.")
            verse_param = None
        else:
            report.line("PASS", L_DEF + f": {verse.name}({params[0].arg})")
            verse_param = params[0].arg

    if verse is None or verse_param is None:
        report.skip(L_PARAM, L_LOOP)
    else:
        # ---- parameter is used
        used = any(is_name(n, verse_param) for n in ast.walk(verse))
        if used:
            report.line("PASS", L_PARAM)
        else:
            report.line("FAIL", L_PARAM,
                        f"{verse.name}() never uses {verse_param}. Every verse would come out\n"
                        f"the same. Use {verse_param} where the word that changes goes.")

        # ---- for loop over range(REPEAT)
        fors = [n for n in ast.walk(verse) if isinstance(n, ast.For)]
        whiles = [n for n in ast.walk(verse) if isinstance(n, ast.While)]
        good = [f for f in fors if is_range_repeat(f.iter)]
        if good:
            report.line("PASS", L_LOOP)
        elif fors and any(is_call_to(f.iter, "range") for f in fors):
            line = next(f for f in fors if is_call_to(f.iter, "range")).lineno
            report.line("FAIL", L_LOOP,
                        f"Line {line} has a range(), but not range(REPEAT).\n"
                        "Use the REPEAT constant instead of typing the number.")
        elif whiles:
            report.line("FAIL", L_LOOP,
                        f"Line {whiles[0].lineno} uses while. This lab practices a for loop\n"
                        "with range(REPEAT).")
        else:
            report.line("FAIL", L_LOOP,
                        f"Inside {verse.name}(), the first two lines of a verse happen REPEAT\n"
                        "times. Let a for loop with range(REPEAT) do the repeating.")

    # ---- doo-doo typed once
    docstrings = set()
    for owner in [tree] + [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        first = owner.body[0] if owner.body else None
        if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)):
            docstrings.add(id(first.value))
    doo_nodes = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Constant) and isinstance(n.value, str)
                 and "doo-doo" in n.value and id(n) not in docstrings]
    doo_nodes.sort(key=lambda n: n.lineno)
    if len(doo_nodes) <= 1:
        report.line("PASS", L_DOO)
    else:
        lines = ", ".join(str(n.lineno) for n in doo_nodes[:6])
        more = " ..." if len(doo_nodes) > 6 else ""
        report.line("FAIL", L_DOO,
                    f"The doo-doo line is typed {len(doo_nodes)} times (lines {lines}{more}).\n"
                    "Once your verse-maker works, it should be the only place it's typed.")

    # ---- main() makes three calls and nothing else
    if main_node is None:
        report.line("FAIL", L_MAIN,
                    "def main(): is missing. Keep  def main():  and put your calls inside it,\n"
                    "indented one step. If you need the original, it's in the class template:\n"
                    f"{TEMPLATE_URL}")
        return
    body = body_without_docstring(main_node)
    prints = [s for s in body if isinstance(s, ast.Expr) and is_call_to(s.value, "print")]
    if verse is None:
        report.line("FAIL", L_MAIN,
                    "main() can't call the verse-maker until there is one. See the line above.")
        return
    calls = [s for s in body if isinstance(s, ast.Expr) and is_call_to(s.value, verse.name)]
    others = [s for s in body if s not in calls]
    if prints:
        report.line("FAIL", L_MAIN,
                    f"main() still has {len(prints)} print lines. Once {verse.name}() works,\n"
                    "main() doesn't print anything itself. It just calls "
                    f"{verse.name}(), once per verse.")
    elif others:
        report.line("FAIL", L_MAIN,
                    f"Line {others[0].lineno} in main() isn't a call to {verse.name}().\n"
                    f"main() should be three lines, each one calling {verse.name}().")
    elif len(calls) != 3:
        report.line("FAIL", L_MAIN,
                    f"main() calls {verse.name}() {len(calls)} times. The song has three verses.")
    elif any(len(c.value.args) != 1 or c.value.keywords for c in calls):
        bad = next(c for c in calls if len(c.value.args) != 1 or c.value.keywords)
        report.line("FAIL", L_MAIN,
                    f"Line {bad.lineno}: each call should pass exactly one value,\n"
                    "the word for that verse.")
    else:
        report.line("PASS", L_MAIN)


def check_guard(report, tree):
    doc = module_docstring(tree)
    loose = []
    guard_found = False
    for stmt in tree.body:
        if stmt is doc:
            continue
        if isinstance(stmt, (ast.FunctionDef, ast.Assign, ast.Import, ast.ImportFrom)):
            continue
        if is_main_guard(stmt) and not guard_found:
            guard_found = True
            continue
        loose.append(stmt)

    if loose:
        report.line("FAIL", L_GUARD,
                    f"Line {loose[0].lineno} runs on its own, outside main().\n"
                    "Move it inside main(), or delete it if main() already does that job.")
    elif not guard_found:
        report.line("FAIL", L_GUARD,
                    "The last two lines of the file should be:\n"
                    "    if __name__ == \"__main__\":\n"
                    "        main()\n"
                    f"Copy them back from the class template:\n{TEMPLATE_URL}")
    elif not is_main_guard(tree.body[-1]):
        report.line("FAIL", L_GUARD,
                    "Keep  if __name__ == \"__main__\":  as the last thing in the file.")
    else:
        report.line("PASS", L_GUARD)


def check_code(report):
    report.heading("Toolchain")
    version = ".".join(str(p) for p in sys.version_info[:3])
    report.line("PASS", f"Python is installed ({version})")

    if not MAIN.exists():
        report.line("FAIL", "main.py is in this folder",
                    "Use File > Open Folder and open the whole BabyShark folder,\n"
                    "not a single file.")
        return
    report.line("PASS", "main.py is in this folder")

    report.heading("Your code")
    source = MAIN.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source)
    except SyntaxError as err:
        report.skip(L_NAME)
        report.line("FAIL", L_SYNTAX,
                    f"Python can't read line {err.lineno}: {err.msg}\n"
                    "Look for a missing colon, parenthesis, or quote, and check that\n"
                    "everything inside a def or a for is indented one more step.")
        report.skip(*AFTER_SYNTAX)
        return

    check_name(report, tree)
    report.line("PASS", L_SYNTAX)
    check_song(report)
    check_repeat(report, tree)
    check_structure(report, tree)
    check_guard(report, tree)


# ---------------------------------------------------------------- git checks

def check_git(report):
    report.heading("Git and GitHub")

    if not shutil.which("git"):
        report.line("FAIL", "Git is installed",
                    "Close every terminal, then close and reopen VS Code.\n"
                    "If that doesn't fix it, reinstall Git from Assignment 1.")
        report.skip("This folder is a Git repository", "Your copy is on your own GitHub account",
                    "Your code is committed", "Your commit is pushed to GitHub")
        return
    report.line("PASS", "Git is installed")

    ok, _ = run_git("rev-parse", "--is-inside-work-tree")
    if not ok:
        report.line("FAIL", "This folder is a Git repository",
                    "This folder wasn't cloned with git clone.\n"
                    "Did you download the ZIP? Go back to step 2 in README.md.")
        report.skip("Your copy is on your own GitHub account",
                    "Your code is committed", "Your commit is pushed to GitHub")
        return
    report.line("PASS", "This folder is a Git repository")

    ok, url = run_git("config", "--get", "remote.origin.url")
    if not ok or "github.com" not in url.lower():
        report.line("FAIL", "Your copy is on your own GitHub account",
                    "This folder isn't connected to GitHub.\n"
                    "Go back to step 2 in README.md and clone YOUR copy.")
        report.skip("Your code is committed", "Your commit is pushed to GitHub")
        return
    if "github.com/cs1430/" in url.lower() or "github.com:cs1430/" in url.lower():
        report.line("FAIL", "Your copy is on your own GitHub account",
                    "You cloned the CLASS template, not your own copy.\n"
                    "Go back to step 1 in README.md: Use this template > Create a new repository.")
        report.skip("Your code is committed", "Your commit is pushed to GitHub")
        return
    report.line("PASS", "Your copy is on your own GitHub account")

    ok_root, roots = run_git("rev-list", "--max-parents=0", "HEAD")
    ok_status, status = run_git("status", "--porcelain", "--", "main.py")
    changed_since_template = False
    if ok_root and roots:
        root = roots.splitlines()[0]
        same, _ = run_git("diff", "--quiet", root, "HEAD", "--", "main.py")
        changed_since_template = not same
    if ok_status and status:
        report.line("FAIL", "Your code is committed",
                    "main.py has changes that aren't committed yet.\n"
                    "Save (Ctrl+S), then in Source Control type a message and click Commit.")
        report.skip("Your commit is pushed to GitHub")
        return
    if not changed_since_template:
        report.line("FAIL", "Your code is committed",
                    "Your code isn't in a commit yet. Save (Ctrl+S), then in\n"
                    "Source Control type a message and click Commit.")
        report.skip("Your commit is pushed to GitHub")
        return
    report.line("PASS", "Your code is committed")

    ok_local, local = run_git("rev-parse", "HEAD")
    ok_remote, remote = run_git("ls-remote", "origin", "HEAD", timeout=30)
    if not ok_remote:
        report.line("FAIL", "Your commit is pushed to GitHub",
                    "Could not reach GitHub to check. Make sure you're online,\n"
                    "then run this file again.")
        return
    remote_sha = remote.split()[0] if remote else ""
    if ok_local and local == remote_sha:
        report.line("PASS", "Your commit is pushed to GitHub")
    else:
        report.line("FAIL", "Your commit is pushed to GitHub",
                    "Committing saves your work on this computer. PUSH sends it\n"
                    "to GitHub. Click Sync Changes (or run git push), then run this file again.")


def main():
    print(_paint("CS 1430 Baby Shark checker", "1"))
    report = Report()
    check_code(report)
    check_git(report)
    print()
    if report.failed:
        print("Fix the FIRST line that says FAIL, save, and run this file again.")
    else:
        print(_paint("All checks passed. Doo-doo-doo-do-do-do-do.", "32"))


if __name__ == "__main__":
    main()
