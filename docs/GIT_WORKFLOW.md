# Git workflow — how changes reach GitHub

**Prerequisites:** Git installed and the repository created — both
covered in [`01-setup.md`](01-setup.md). You can read this document
before doing either.

**Learning goal:** after this you will know what Git actually is, what
a branch actually is, why this project uses three of them, and you will
be able to run the end-of-phase ritual without copying it blindly.

> Every term here is also in [`GLOSSARY.md`](GLOSSARY.md).

---

## 1. What Git is, if you have never used it

**Git is a save-game system for your work.**

In a video game you save before the difficult bit. If it goes wrong you
reload. You do not fear the difficult bit, because the save exists.

Git does this for files. You decide when to save (a **commit**), each
save is permanent and labelled with a message, and you can return to
any of them. The consequence is bigger than it sounds: **you can stop
being careful.** Delete a chunk of code to see if it was needed. Try
the risky refactor. The save exists.

Compare the alternative, which almost everyone has done at least once:

```
analysis.py
analysis_v2.py
analysis_v2_fixed.py
analysis_FINAL.py
analysis_FINAL_use_this_one.py
```

That is version control implemented by hand, badly. It records no
reasons, no dates, no way to see what actually changed between two
files, and no way to combine work.

**GitHub** is a website that stores a copy of your Git repository
online. Git is the camera; GitHub is the shared album. Git works
perfectly well with no GitHub at all — the history is on your machine.
GitHub adds backup, sharing and a public home for the work.

---

## 2. The three places a change can be

This trips up nearly everyone at first, so it is worth thirty seconds.
A change passes through three states:

```
   your files            the staging area           the history
  (working tree)             (index)                  (commits)
        |                       |                        |
        |  ---- git add ---->   |                        |
        |                       |  ---- git commit --->  |
        |                       |                        |
                                                    --- git push --->  GitHub
```

- **Working tree** — the files as they are right now on disk. You edit
  here.
- **Staging area** — the changes you have chosen to include in your next
  save. *Analogy:* items on the supermarket checkout belt. Selected,
  not yet paid for.
- **History** — the permanent record of commits. *Analogy:* the
  receipts.

**Why the middle step exists.** Because you often change five things
and only three belong together. Staging lets you commit those three
with one clear message and the other two separately. In this project
you will usually stage everything at once (`git add -A`), which is fine
and normal for solo work — but now you know why the step is there.

---

## 3. What a branch is

**A branch is an independent line of work.**

*Analogy.* You are writing an important document. You keep a clean copy
you would be happy for anyone to read, and you also keep a working
draft where you rewrite whole sections, try a different structure and
occasionally make it worse. Both exist at the same time. When the draft
is genuinely better, it becomes the clean copy.

Git makes that first-class. Your files can exist in several versions
simultaneously, each on its own branch, and you switch between them
with one command. When you switch, the files on disk change to match
that branch.

**A branch is not a folder.** There is only ever one set of files in
your project directory. Switching branches rewrites them to match.
Beginners often expect three folders for three branches; there is one
folder that changes contents.

---

## 4. This project's three branches

| Branch | Purpose | Analogy |
|---|---|---|
| **`develop`** | Where all work happens. Half-finished things live here. | The workbench |
| **`beta`** | A checkpoint copy — what a tester would try. | The demonstration model |
| **`master`** | The published, presentable state. | The showroom |

All three are created from the same starting point and all three are
pushed together at the end of each phase.

### "Why three branches when I am one person?"

An honest question, and the honest answer has three parts.

1. **It separates working from published.** Even solo, there is real
   value in "the thing I am fiddling with" being distinct from "the
   thing someone might look at right now".
2. **It is the habit teams use.** Nearly every professional repository
   separates work-in-progress from released. Building the reflex on a
   solo project costs one extra line per phase and means you already
   have it when you need it.
3. **It gives you two fallbacks.** If `develop` gets into a mess, both
   `beta` and `master` still hold a known-good state you can return to.

### Why `master` and not `main`

GitHub's default for new repositories is `main`; the older, and still
extremely widespread, convention is `master`. This project uses
`master` deliberately and consistently. Neither is more correct — what
matters is that your documentation says which one you use, so anyone
following it does not hit a wall. This document is that.

---

## 5. Creating the three branches (one time only)

Do this once, when the repository is first created. `01-setup.md` walks
through it in context; this is the reference version.

```bash
# 1. Inside your project folder, start tracking it with Git.
git init

# 2. Name the first branch 'master' rather than accepting the default.
git branch -M master

# 3. Make the first commit, so the branches have something to point at.
#    (A branch must point at a commit; you cannot branch from nothing.)
git add -A
git commit -m "chore: initial project structure and documentation"

# 4. Connect this folder to your empty GitHub repository.
#    Replace the URL with your own.
git remote add origin https://github.com/YOURNAME/realsignal.git

# 5. Push master and record the connection ( -u ) so future pushes are shorter.
git push -u origin master

# 6. Create beta and develop, both starting from exactly where master is.
git branch beta
git branch develop

# 7. Publish them both to GitHub.
git push -u origin beta
git push -u origin develop

# 8. Move onto develop — from now on, this is where you work.
git switch develop
```

**Expected output of the last command:**

```
Switched to branch 'develop'
Your branch is up to date with 'origin/develop'.
```

**Verify all three exist**, locally and on GitHub:

```bash
git branch -a
```

```
* develop
  beta
  master
  remotes/origin/beta
  remotes/origin/develop
  remotes/origin/master
```

The `*` marks the branch you are on. If you see all six lines, the
setup is correct.

---

## 6. The end-of-phase ritual

This is the block that appears at the end of every phase document. Run
it whenever you reach a checkpoint that works.

```bash
# 1. Make sure you are on the working branch.
git switch develop

# 2. Stage every change in the project (new, modified and deleted files).
git add -A

# 3. Save them permanently, with a message explaining what changed.
git commit -m "Phase 1: verified download of published dataset"

# 4. Send develop to GitHub, and update beta and master to match it.
git push origin develop develop:beta develop:master

# 5. Bring your local master up to date with the master you just pushed.
git switch master
git pull --ff-only origin master

# 6. Return to the working branch, ready for the next phase.
git switch develop
```

### What each part actually means

**`git switch develop`** — move to the working branch. Safe to run even
if you are already there; it will simply say so. Running it every time
turns "which branch am I on?" from a question into a non-issue.

**`git add -A`** — stage everything. The `-A` means *all* changes,
including files you deleted (a common omission with plain `git add .`
in older Git versions).

**`git commit -m "..."`** — create the permanent save point. The
message is not decoration; it is what you or a stranger reads in six
months to understand *why* something changed. See §7.

**`git push origin develop develop:beta develop:master`** — the
interesting line. It does three things in one command:

- `develop` — push local `develop` to remote `develop`.
- `develop:beta` — push local `develop` *to remote* `beta`. The colon
  means "take what's on the left, put it on the branch named on the
  right".
- `develop:master` — same, onto remote `master`.

So all three remote branches end up pointing at the same, tested state,
in one operation.

*Analogy:* you finish the draft, and simultaneously file it as the
draft, the review copy, and the published copy — because at this
checkpoint, all three should say the same thing.

**`git switch master` then `git pull --ff-only origin master`** — step
5 exists because of a real subtlety. The previous command updated
`master` **on GitHub**, but your *local* `master` branch still points at
the old commit. It does not update itself. This step brings it in line,
so your local repository is not quietly inconsistent with the remote.

The `--ff-only` flag means **fast-forward only**: *only update if it is
a clean, no-surprises move forward; otherwise stop and tell me.* If
local `master` had diverged, Git refuses rather than silently creating
a merge you did not ask for.

*Analogy:* a rule that says "you may only move the bookmark forward
through the book, never sideways into a different book". If something
does not fit that description, you want to be told, not helped.

**`git switch develop`** — return to the workbench. Always end here, so
your next session starts in the right place. Making an edit while
accidentally on `master` is the most common way a solo Git history gets
tangled, and always finishing on `develop` prevents it.

### The optional tag line

Occasionally — at a release, not at every phase — you will want a
permanent name pinned to a commit:

```bash
git tag -a v1.0.0 -m "First complete release"
git push origin develop develop:beta develop:master --tags
```

`--tags` sends the tags along. Use it only when you have created a tag;
there is no need for it in normal phase commits.

---

## 7. Writing commit messages that are worth reading

A commit message answers: *what changed, and why?* The what is often
visible in the code; the why almost never is.

**A convention worth adopting** (used throughout this project) is a
short type prefix:

| Prefix | Use for |
|---|---|
| `feat:` | A new capability |
| `fix:` | Correcting something broken |
| `docs:` | Documentation only |
| `test:` | Adding or changing tests |
| `chore:` | Housekeeping — dependencies, structure, configuration |
| `refactor:` | Restructuring code without changing behaviour |

**Good:**

```
feat: download and checksum-verify the published dataset
fix: handle strains recorded as ambiguous rather than dropping the row
docs: explain why the raw data folder is never edited
```

**Poor:**

```
update
stuff
fixed it
asdf
```

The test: would this message help a stranger — or you in six months —
understand why this commit exists, without reading the code?

---

## 8. The five situations that will confuse you, and their fixes

Everyone hits these. They are not signs of failure.

### "I edited files but I'm on the wrong branch"

You made changes while on `master` instead of `develop`. Nothing is
lost:

```bash
git stash          # put the changes safely to one side
git switch develop # go where you meant to be
git stash pop      # bring the changes back, now on develop
```

*Analogy:* picking up your papers, walking to the right desk, putting
them down again.

### "It says my branch is behind / has diverged"

The remote has commits your local branch does not. Usually because you
edited a file directly on the GitHub website. Fix:

```bash
git switch develop
git pull --ff-only origin develop
```

If `--ff-only` refuses, the branches have genuinely diverged and you
must decide which changes to keep. Do not guess — read what Git printed;
it names the branches and commits involved.

### "It won't let me push"

Almost always because the remote has something you do not. Pull first
(as above), then push. **Never** reach for `--force` to make an error
message go away: force-pushing overwrites history on GitHub, and the
overwritten commits are genuinely gone.

### "I committed something I shouldn't have" (data, a secret)

If it is **not yet pushed**:

```bash
git reset --soft HEAD~1   # undo the commit, keep the file changes
```

Then add the file to `.gitignore` and commit again. If it **is** pushed
and it is a secret — a password or key — the only safe assumption is
that it is compromised: revoke and replace it. Removing it from
history is possible but fiddly, and revoking is what actually protects
you.

This is precisely why `.gitignore` lists `data/` and environment files
*before* the first commit rather than after.

### "Git is asking me to configure my name"

Once per machine:

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

Every commit records who made it, which is why it asks.

---

## 9. A quick reference card

```bash
git status                 # what has changed? (run this constantly — it is free)
git switch develop         # move to the working branch
git branch -a              # list every branch, local and remote
git add -A                 # stage all changes
git commit -m "msg"        # save them permanently
git log --oneline -10      # the last ten commits, one line each
git diff                   # what changed that isn't staged yet
git push origin develop develop:beta develop:master
git switch master && git pull --ff-only origin master && git switch develop
```

**`git status` is the most useful command in Git.** It tells you which
branch you are on, what has changed, what is staged, and usually
suggests the command you want next. Run it before and after everything
until it becomes reflex. It changes nothing, so it can never do harm.

---

**Next:** [`01-setup.md`](01-setup.md) if you have not set up yet, or
back to [`00-architecture.md`](00-architecture.md) for the system map.
