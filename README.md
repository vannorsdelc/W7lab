# CS 1430 · Baby Shark

`main.py` already sings the whole song, one `print` at a time. Your job is to make the code **shorter and smarter without changing one character of what it prints**. Your instructor explains the task in class.

**You're done when** `check.py` shows PASS on every line. After that, fill in the reflection slide deck.

---

## Before you start

You need the Assignment 1 toolchain: Python, Git, VS Code with the Python extension, and a GitHub account you're signed in to.

---

## Step 1: Make your own copy

1. On this page, click the green **Use this template** button (top right) → **Create a new repository**.
2. **Owner:** your own account, not CS1430.
3. **Repository name:** `BabyShark`
4. **Visibility:** Public
5. Click **Create repository**.

> **Do NOT click Fork.** Use this template only.

---

## Step 2: Clone it to your computer

1. On **your** new repo's page, click the green **Code** button and copy the HTTPS URL.
2. Open VS Code. Open a terminal: **Terminal → New Terminal**.
3. Type this, using **your** URL (not CS1430's), and press Enter:

```
git clone https://github.com/YOUR-USERNAME/BabyShark.git C:\CS1430\BabyShark
```

Keep your work out of Documents, Desktop, and OneDrive.

---

## Step 3: Open the folder in VS Code

1. **File → Open Folder…** and choose `C:\CS1430\BabyShark`. Pick the **whole folder**, not a single file.
2. If VS Code asks whether you trust the authors, click **Yes, I trust the authors**.
3. In the Explorer panel you should see `README.md`, `main.py`, `check.py`, and a few items that start with a dot.

---

## Step 4: Copilot stays quiet in this folder

This folder includes a settings file that turns off Copilot's typing suggestions here, and only here. Leave it that way.

- Don't ask Copilot Chat (or any other AI) to rewrite `main.py`. The point is for **you** to work out the new shape.
- Asking an AI to explain an error message in plain words is fine.

---

## Step 5: Run it first

Open `main.py` and click **▷ Run** (top right). Read the output. Then read the code and look for what repeats.

---

## Step 6: Write your code

| Rule | |
|---|---|
| The output stays **exactly** the same | All 21 lines, every comma and capital |
| Type your name on line 2 | Replace `your name` in the header |
| Leave `REPEAT = 3` and the last two lines of the file alone | `check.py` looks for them |
| `check.py` lists the rest | Read its output. It's your to-do list |

Save the file: **Ctrl + S**.

---

## Step 7: Run the checker

Type this in the terminal:

```
python check.py
```

Under **Git and GitHub**, `Your code is committed` will say **FAIL** until you commit. **That's expected.**

> **Rule of thumb:** fix only the **first** FAIL line, save, and run the checker again.

---

## Step 8: Commit and push

| Save | Where it lives |
|---|---|
| **Saved** (Ctrl + S) | Only this computer |
| **Committed** (a labeled snapshot) | Still only this computer |
| **Pushed** | On GitHub |

**In VS Code:**

1. Click the **Source Control** icon in the left sidebar.
2. Type a short message, like `baby shark done`.
3. Click **✓ Commit**. If VS Code asks about staging changes, click **Yes**.
4. Click **Sync Changes** (or **Push**).

**Prefer the terminal?**

```
git add .
git commit -m "baby shark done"
git push
```

---

## Step 9: Run the checker again

```
python check.py
```

Every line should say **PASS**. Keep this terminal open. You'll screenshot it for the reflection deck.

---

## If something breaks

| You see | Fix |
|---|---|
| `'git' is not recognized` | Close every terminal, then close and reopen VS Code |
| `main.py is in this folder` FAIL | **File → Open Folder** and pick `C:\CS1430\BabyShark` |
| `expected an indented block` or `unindent does not match` | Code that belongs inside a `def` or a `for` goes one step further in than the line above it |
| `Prints all 21 lines` FAIL | The checker names the first line that's different. Run `main.py` and compare that line yourself |
| `NameError` | Check spelling and capitals. Names must match exactly everywhere you use them |
| `REPEAT = 3` or the `__name__` line FAIL | Undo with Ctrl + Z, or copy the original `main.py` from the class template on GitHub |
| `Your copy is on your own GitHub account` FAIL | You cloned the class template. Go back to Step 1 |
| `Your code is committed` FAIL | Step 8, parts 1 to 3 |
| `Your commit is pushed to GitHub` FAIL | Click **Sync Changes**, or run `git push` |
| `python` opens the Microsoft Store | Try `py check.py` instead, then ask your instructor |
