#!/bin/bash
# check-public-safe.sh: is this checkout safe to push to the PUBLIC repository?
#
# Run it from the project folder before every push:
#     ./check-public-safe.sh            (Windows: bash check-public-safe.sh in Git Bash)
#
# Exit 0 = safe to push. Exit 1 = something that must stay private would be published.
#
# It checks exactly what the next commit could publish:
#   * every file Git already tracks, and
#   * every new file that `git add -A` would add (new and not ignored).
# Ignored files (.venv/, data/, .env, .local-notes/ ...) are skipped, because
# Git never adds them unless someone forces it with `git add -f`, and a forced
# file is tracked, so it gets checked. .gitignore prevents accidents; this
# script catches the ones that slip past it. Two locks are better than one.
#
# Explained in docs/01-setup.md, "The safety gate".
# It never changes any file. It only looks and reports.

cd "$(dirname "$0")" || exit 1

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not a Git repository. Run this from the project folder."
  exit 1
fi

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
fail=0

# The files a commit could publish: tracked (--cached) plus new and not ignored.
candidates() { git ls-files --cached --others --exclude-standard "$@" 2>/dev/null; }
# Search the CONTENT of that same set. Plain `git grep` reads tracked files;
# `git grep --untracked` adds the new ones. Together they cover what a commit
# could publish.
gitscan() { { git grep "$@"; git grep --untracked "$@"; } 2>/dev/null | sort -u; }
n_tracked=$(git ls-files | wc -l | tr -d ' ')
n_new=$(git ls-files --others --exclude-standard | wc -l | tr -d ' ')

echo "Checking whether this checkout is safe to publish..."
echo "Scanning ${n_tracked} tracked file(s) and ${n_new} new file(s) that 'git add -A' would add."
echo ""

# ---- 1. Folders and files that must never be published ----------------------
# Environments, downloaded data, private notes and secrets.
echo "1. Environments, data, private notes and secrets"
step1=0
for p in .venv renv/library .env .env.local .Renviron .local-notes data ; do
  found=$(candidates -- "$p")
  if [ -n "$found" ]; then
    echo -e "   ${RED}✗ WOULD BE PUBLISHED: $p${NC}"
    echo "$found" | head -10 | sed 's/^/     /'
    fail=1 ; step1=1
  fi
done
[ $step1 -eq 0 ] && echo -e "   ${GREEN}✓ none${NC}"

# ---- 2. File types that hold secrets, databases or downloaded archives -------
# A force-added file of these types at ANY path. The downloaded archive (.zip)
# belongs in data/raw/, which is never committed: the script fetches it.
echo ""
echo "2. Secret, database and archive file types"
ext=$(candidates | grep -iE '\.(key|pem|crt|cer|p12|pfx|db|sqlite3?|duckdb|dump|bak|zip|part|rds|rdata)$')
if [ -n "$ext" ]; then
  echo -e "   ${RED}✗ these files would be published:${NC}"
  echo "$ext" | sed 's/^/     /'
  fail=1
else
  echo -e "   ${GREEN}✓ none${NC}"
fi

# ---- 3. Text that looks like a real credential --------------------------------
# Real keys have recognisable formats. We match the FORMATS, not the word
# "key", so documents that merely talk about keys don't set off the alarm.
# -w makes git check that a match starts and ends a word, so a link anchor such
# as "#task-..." isn't mistaken for an "sk-..." key. Regular-expression engines
# differ between systems (an earlier version of this check, which used {20,}
# and "^" inside a group, found nothing on macOS), so the pattern uses neither:
# a run of 20 characters is written out in full by repeat() below.
# The script leaves itself out of the search.
echo ""
echo "3. Credential-shaped text"
repeat() { r=""; i=0; while [ $i -lt "$2" ]; do r="$r$1"; i=$((i + 1)); done; printf '%s' "$r"; }
K='[A-Za-z0-9_-]'; A='[A-Za-z0-9]'; W='[A-Za-z0-9_]'
creds=$(gitscan -n -w -E \
  "sk-$(repeat "$K" 20)$K*|ghp_$(repeat "$A" 20)$A*|gho_$(repeat "$A" 20)$A*|github_pat_$(repeat "$W" 20)$W*|AKIA$(repeat '[0-9A-Z]' 16)|-----BEGIN [A-Z ]*PRIVATE KEY-----" \
  -- ':!check-public-safe.sh')
if [ -n "$creds" ]; then
  echo -e "   ${RED}✗ something that looks like a real credential; remove it before pushing:${NC}"
  echo "$creds" | cut -c1-120 | sed 's/^/     /'
  fail=1
else
  echo -e "   ${GREEN}✓ none found${NC}"
fi

# ---- 4. Paths that only exist on one computer ---------------------------------
# /Users/<name>/, /home/<name>/ or C:\Users\<name>\ reveals a machine and
# breaks the project for anyone else. Write examples as /Users/<you>/... and
# use paths relative to the project folder in code.
echo ""
echo "4. Paths from one particular computer"
paths=$(gitscan -inE '/Users/[A-Za-z0-9._-]+/|/home/[A-Za-z0-9._-]+/|[A-Za-z]:\\\\Users\\\\' \
  -- ':!check-public-safe.sh')
if [ -n "$paths" ]; then
  echo -e "   ${RED}✗ machine-specific path(s); use a relative path or <you> instead:${NC}"
  echo "$paths" | cut -c1-120 | sed 's/^/     /'
  fail=1
else
  echo -e "   ${GREEN}✓ none found${NC}"
fi

# ---- 5. Operating-system clutter ------------------------------------------------
# macOS writes .DS_Store files into every folder you open in Finder; Windows
# writes Thumbs.db and desktop.ini. They can list the names of files nearby,
# and they mean nothing to anyone else.
echo ""
echo "5. Operating-system clutter"
clutter=$(candidates | grep -E '(^|/)(\.DS_Store|Thumbs\.db|desktop\.ini)$')
if [ -n "$clutter" ]; then
  echo -e "   ${RED}✗ clutter files would be published:${NC}"
  echo "$clutter" | sed 's/^/     /'
  echo "     Fix: git rm --cached <file> for each one (they stay on disk; .gitignore keeps them out from then on)"
  fail=1
else
  echo -e "   ${GREEN}✓ none${NC}"
fi

# ---- 6. Hidden records inside images ---------------------------------------------
# A picture can carry records nobody sees on screen: the GPS position where a
# photo was taken (EXIF), or a record left by the program that last edited or
# exported it ("content credentials", C2PA). This project's pictures are drawn
# by its own scripts, so a flagged file is redrawn, not edited.
echo ""
echo "6. Hidden records inside images"
hidden=$(candidates | grep -iE '\.(png|jpe?g|gif|webp|svg|tiff?|pdf)$' | while read -r f; do
           [ -f "$f" ] || continue
           LC_ALL=C grep -a -q -i -E 'c2pa|GPSLatitude|exif:GPS' "$f" && echo "$f"
         done)
if [ -n "$hidden" ]; then
  echo -e "   ${RED}✗ these pictures carry hidden records:${NC}"
  echo "$hidden" | sed 's/^/     /'
  echo "     Fix: redraw them (python figures/make_concept_figures.py, python figures/make_illustrations.py),"
  echo "     or for a picture from elsewhere, export a fresh copy without metadata"
  fail=1
else
  echo -e "   ${GREEN}✓ none${NC}"
fi

# ---- 7. Large files (information only) ------------------------------------------
echo ""
echo "7. Large files (information only)"
big=$(candidates | while read -r f; do
        [ -f "$f" ] || continue
        sz=$(wc -c <"$f" 2>/dev/null)
        if [ "${sz:-0}" -gt 5242880 ]; then
          awk -v s="$sz" -v f="$f" 'BEGIN{printf "     %6.1f MB  %s\n", s/1048576, f}'
        fi
      done)
if [ -n "$big" ]; then
  echo -e "   ${YELLOW}! files over 5 MB would be published. Is that intended?${NC}"
  echo "$big"
else
  echo -e "   ${GREEN}✓ nothing oversized${NC}"
fi

# ---- 8. Your name and handle (information only) -----------------------------------
# Your name and GitHub handle in README, LICENSE and links are intended. This
# lists where they appear, so nothing new creeps in unnoticed.
echo ""
echo "8. Name and handle (information only; fine where intended)"
attr=$(gitscan -inE 'akannan2987|abhilash' -- ':!check-public-safe.sh' | cut -c1-100)
if [ -n "$attr" ]; then
  echo "$attr" | sed 's/^/     /'
else
  echo -e "   ${GREEN}✓ none${NC}"
fi

echo ""
if [ $fail -eq 0 ]; then
  echo -e "${GREEN}✓ SAFE TO PUSH to the public repository${NC}"
  exit 0
fi
echo -e "${RED}✗ NOT SAFE TO PUSH: fix the items marked ✗ above${NC}"
exit 1
