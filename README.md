# Devloop Project Starter

A ready-to-use template for projects watched by [Devloop](https://github.com/rachid-log/devloop),
plus a cheat sheet of every command you need.

Devloop looks at your projects every hour. For each active project, an AI agent proposes
**one** improvement. You approve or reject it in Telegram. Approved work is written on its
own branch, and it is merged only when you ask.

```text
every hour:  watch -> observe -> (you approve) -> execute -> commit -> (you ask) -> merge
```

---

## 1. Add a new project

Pick one of the two ways.

**A. With the command (recommended)**

```bash
devloop init ~/DEV/my-app --domain UX/UI --goal "Make the checkout page easier to use"
devloop watch          # register it and sync it to n8n
devloop projects       # check it is in the list
```

Add `--git` if the folder is not a Git repo yet.

**B. By copying this starter**

```bash
cp .watched.json .gitignore ~/DEV/my-app/
# edit ~/DEV/my-app/.watched.json, then:
devloop watch
```

The project folder must sit somewhere under `DEV_ROOT` (default `~/DEV`).
Devloop finds projects by looking for a `.watched.json` file.

## 2. The `.watched.json` file

```json
{
  "name": "My App",
  "goal": "Improve reliability and user experience",
  "domain": "General",
  "watch_freq": "1h",
  "active": true
}
```

| Field | What it means |
| --- | --- |
| `name` | Display name. Optional: the folder name is used if empty. |
| `goal` | What the agent should care about. Be specific: it shapes every proposal. |
| `domain` | `General`, `UX/UI`, `SEO`, `BL` (business logic) or `Security`. |
| `watch_freq` | Saved for the future. Today every active project is checked each hour. |
| `active` | Start value only. After the first `devloop watch`, the n8n table decides. |

Rules:

- It must be **one JSON object** `{ ... }`, not a list `[ ... ]` and not an empty file.
  Otherwise Devloop skips the project with a warning.
- Commit `.watched.json` in the project repo.

## 3. Turn a project on or off

The switch lives in n8n, not in the file:

**n8n → Overview → Data tables → `devloop_projects` → column `active`** (`true` / `false`).

```bash
devloop projects --all --remote   # ● = on, ○ = off (reads the n8n switch)
```

## 4. Daily commands

All commands work from any folder.

### See what is going on

| Command | What it does |
| --- | --- |
| `devloop status` | All tasks, grouped by status. |
| `devloop status --active` | Only tasks that need you. |
| `devloop status --repo my-app` | Tasks of one project. |
| `devloop show <task-id>` | One task: details and the end of its log. |
| `devloop logs <task-id> --follow` | Watch a task log live. |
| `devloop projects --all --remote` | Projects and whether they are on. |
| `devloop doctor` | Check Git, agents, n8n, Telegram and the models in use. |

### Decide

You can use the Telegram buttons, or these commands. Both do the same thing.

| Command | Telegram button | What it does |
| --- | --- | --- |
| `devloop approve <task-id>` | ✅ Approve | The task is built in the next hourly cycle. |
| `devloop reject <task-id> --reason "..."` | ❌ Reject | The task is closed. |
| `devloop merge <task-id>` | 🚀 Merge to main & Push | Merge the finished branch into main and push. The command does it now; the button does it in the next cycle. |
| (keep the branch) | 👀 Keep Branch | Do nothing yet. The branch stays for you to review. |
| `devloop retry <task-id>` | 🔄 Retry | A failed task runs again in the next cycle. |
| (close it) | ❌ Dismiss | A failed task is closed. |

### Run things now instead of waiting for the hour

```bash
devloop observe --repo my-app          # ask for a proposal now
devloop execute --task <task-id>       # build an approved task now
devloop loop                           # one full cycle now
systemctl --user start devloop.service # one full cycle now, in the background
```

## 5. The hourly timer

```bash
systemctl --user list-timers devloop.timer    # when is the next run
journalctl --user -u devloop.service -f       # watch the runs live
systemctl --user disable --now devloop.timer  # stop the hourly runs
systemctl --user enable --now devloop.timer   # start them again
```

## 6. Rules you can rely on

- **A human approves every task.** Devloop never approves its own work.
- **One open task per project.** While a task waits for your answer, Devloop proposes
  nothing new for that project. It keeps working on the other projects.
- **Work happens on its own branch:** `devloop/<task-id>`. Your main branch is not touched
  until you ask for a merge.
- **Your unsaved work is kept.** Uncommitted changes are put in `git stash` first.
  The stash name is written in the task details.
- **A failed task leaves nothing behind.** If the agent fails, runs out of time
  (`DEVLOOP_EXECUTE_TIMEOUT`, 20 min here) or writes no code, the branch is deleted and you
  get a Telegram message with Retry and Dismiss.
- **No force-push, ever.**

## 7. Settings

Settings live in the `.env` file of the Devloop repo (not in your project).

| Setting | What it does |
| --- | --- |
| `DEVLOOP_RUNNER` | Which agent CLI runs: `claude` or `agy`. |
| `DEVLOOP_OBSERVE_MODEL` | Model that proposes tasks, e.g. `claude-sonnet-5-5`. |
| `DEVLOOP_EXECUTE_MODEL` | Model that writes the code, e.g. `claude-opus-5-5`. |
| `DEVLOOP_OBSERVE_TIMEOUT` | Seconds allowed for a proposal. |
| `DEVLOOP_EXECUTE_TIMEOUT` | Seconds allowed to write the code. |
| `DEVLOOP_DIRTY_POLICY` | Uncommitted work: `stash` (default), `abort` or `reset`. |
| `DEV_ROOT` | Folder scanned for projects. |

After editing `.env`, run `devloop doctor` to check the result.

## 8. When something looks wrong

| Problem | Fix |
| --- | --- |
| My project is not in `devloop projects` | Check `.watched.json` is one valid JSON object, then `devloop watch`. |
| It is listed but never gets proposals | It is off in n8n, or a task of it is still waiting for you (`devloop status --repo my-app`). |
| A task failed | `devloop show <task-id>` shows why. Then `devloop retry <task-id>` or Dismiss. |
| Task says "timed out" | The task was too big for the time limit. Split it, or raise `DEVLOOP_EXECUTE_TIMEOUT`. |
| No Telegram messages | `devloop doctor`, and look at the Telegram lines. |
| `devloop: command not found` | Link it: `ln -s ~/DEV/LAB/devloop/.venv/bin/devloop ~/.local/bin/devloop`. |
