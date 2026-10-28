# VeriSafe - Contributing Guide & Team Workflow

Welcome to the **VeriSafe** project by **Team Shadow Paradox**!

This guide outlines our collaborative development workflow. It is designed to allow two developers to work effectively in parallel on separate Git branches, review each other's changes, avoid merge conflicts, and maintain high code quality throughout the hackathon.

---

## 1. Core Principles

1. **`main` Branch is Sacred:** The `main` branch must always remain stable, buildable, and test-passing.
2. **No Direct Commits to `main`:** All work must be conducted on feature branches and integrated via GitHub Pull Requests (PRs).
3. **One Developer Codes, One Reviews:** Every pull request requires review and explicit approval from the other teammate before merging.
4. **No Secrets in Git:** Never commit `.env` files, API keys, credentials, or private certificates.

---

## 2. Branching Strategy

To keep work organized and prevent collision, use standardized branch naming prefixes:

| Branch Type | Prefix & Format | Example | Use Case |
| :--- | :--- | :--- | :--- |
| **New Features** | `feature/<short-description>` | `feature/message-analyzer` | Implementing new frontend or backend capabilities |
| **Bug Fixes** | `fix/<short-description>` | `fix/url-parser-null-check` | Resolving an identified bug or edge case |
| **Documentation**| `docs/<short-description>` | `docs/api-examples` | Updating specifications, guides, or README |
| **Testing** | `test/<short-description>` | `test/url-detection-suite` | Adding or refactoring test cases |
| **Refactoring** | `refactor/<short-description>`| `refactor/rule-engine` | Code reorganization without functional changes |

---

## 3. End-to-End Developer Workflow

### Step 1: Sync Your Local `main`
Before starting any new task, ensure your local `main` branch is completely up to date with GitHub:

```bash
git checkout main
git pull origin main
```

### Step 2: Create a Dedicated Feature Branch
Branch off `main` using the appropriate naming convention:

```bash
# Developer 1 working on backend message analysis:
git checkout -b feature/message-analyzer

# Developer 2 working on frontend submission form:
git checkout -b feature/submission-ui
```

### Step 3: Make Small, Focused Commits
Group related changes into logical commits with descriptive messages following the [Conventional Commits](https://www.conventionalcommits.org/) pattern:

- `feat: add heuristic detection for urgency keywords`
- `fix: handle edge case where URL lacks explicit protocol`
- `docs: update API spec with error response samples`
- `test: add unit test for homoglyph detection`

```bash
git add <files>
git commit -m "feat: add heuristic detection for urgency keywords"
```

### Step 4: Keep Your Branch Synchronized
If your teammate merges a branch into `main` while you are still working, pull the latest changes into your feature branch to avoid major merge conflicts later:

```bash
git fetch origin
git merge origin/main
# Alternatively, use git rebase origin/main if preferred
```

### Step 5: Push Branch and Open a Pull Request
Push your feature branch to GitHub:

```bash
git push -u origin feature/message-analyzer
```

Open a Pull Request on GitHub targeting `main`:
- **Title:** Clear and concise (e.g., `feat: Implement message analysis heuristic engine`).
- **Description:** Provide a summary using the PR template below.

---

## 4. Pull Request Template & Checklist

When opening a PR, include the following details in the description:

```markdown
### What does this PR do?
- Implements the initial keyword-based urgency detector.
- Adds regex-based OTP/credential request matching.

### How to test:
1. Run `pytest tests/test_message_analyzer.py`.
2. Send sample payload to `/api/messages/analyze` using curl or Postman.

### Checklist:
- [ ] Code follows existing project style and conventions.
- [ ] No extraneous files or secrets committed.
- [ ] Tests added/updated and passing locally.
- [ ] PR reviewed and approved by teammate.
```

---

## 5. Code Review Process (Two-Developer Model)

Both team members share equal ownership of the codebase. The peer-review workflow ensures both developers understand all parts of the application:

1. **Review Request:** Assign your teammate as the reviewer upon opening the PR.
2. **Reviewer Responsibility:**
   - Verify that the code satisfies the intended task without breaking existing functionality.
   - Check that error handling and validation constraints are respected.
   - Confirm no sensitive data or temporary files are included.
   - Test locally if the change is substantial.
3. **Leaving Feedback:**
   - Use GitHub comments to ask questions, suggest improvements, or point out bugs.
   - Be constructive, clear, and focused on code quality and project goals.
4. **Approval & Merging:**
   - Once all review comments are addressed, the reviewer approves the PR.
   - The author or reviewer clicks **Squash and Merge** (or **Merge Pull Request**) to integrate changes cleanly into `main`.
   - Delete the remote feature branch on GitHub.

---

## 6. Post-Merge Cleanup

After a PR is merged, clean up your local workspace:

```bash
# Return to main and fetch latest merged state
git checkout main
git pull origin main

# Delete the local feature branch that was merged
git branch -d feature/message-analyzer

# Prune stale remote-tracking branches
git remote prune origin
```

---

## 7. Resolving Merge Conflicts

If both developers happen to edit the same file or lines simultaneously, a merge conflict will occur. Resolve it collaboratively:

1. Fetch the latest `main`:
   ```bash
   git fetch origin
   git merge origin/main
   ```
2. Git will mark conflict sections in affected files:
   ```text
   <<<<<<< HEAD (Current change)
   const API_BASE = "http://localhost:8000/api";
   =======
   const API_BASE = process.env.VITE_API_URL || "/api";
   >>>>>>> origin/main (Incoming change)
   ```
3. Communicate directly with your teammate to decide on the correct unified implementation.
4. Remove conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`), save the file, and verify:
   ```bash
   git add <resolved-file>
   git commit -m "chore: resolve merge conflicts with main"
   git push origin <your-feature-branch>
   ```

---

## 8. Division of Responsibilities (Recommended Hackathon Split)

To minimize conflicts, divide domain responsibilities clearly:

- **Developer A (Backend / Analysis Engine):**
  - REST endpoints (`/api/messages/analyze`, `/api/urls/analyze`, `/api/health`).
  - Detection logic, heuristics, and regex/NLP models in `backend/`.
  - Backend unit and integration tests in `tests/`.

- **Developer B (Frontend / User Interface):**
  - UI components and layout in `frontend/`.
  - API client integration and state management.
  - User experience, result visualization, and indicator displays.

