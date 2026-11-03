# Devloop Project Starter

A ready-to-use template for projects watched by [Devloop](https://github.com/rachid-log/devloop),
plus a cheat sheet of every command you need.

Every 10 minutes Devloop looks at your idle projects. For each one, an AI agent proposes
**one** improvement. You approve or reject it in Telegram. Approved work is written on its
own branch, in its own folder, and it is merged only when you ask.

```text
every 10 min:  watch -> observe -> (you approve)
every 2 min:   execute -> commit -> (you ask) -> merge
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
  "active": true,
  "observe_effort": "high"
}
```

| Field | What it means |
| --- | --- |
| `name` | Display name. Optional: the folder name is used if empty. |
| `goal` | What the agent should care about. Be specific: it shapes every proposal. |
| `domain` | `General`, `UX/UI`, `SEO`, `BL` (business logic) or `Security`. |
| `watch_freq` | Minimum time between two proposals: `10m`, `1h`, `1d`... |
| `active` | Start value only. After the first `devloop watch`, Telegram (`/projects`) decides. |
| `observe_model`, `observe_effort` | Optional. Model and effort that propose tasks for this project. |
| `execute_model`, `execute_effort` | Optional. Model and effort that write the code for this project. |

Effort is one of `low`, `medium`, `high`, `xhigh`, `max`. Empty optional fields use the
values in the Devloop `.env`.

Rules:

- It must be **one JSON object** `{ ... }`, not a list `[ ... ]` and not an empty file.
  Otherwise Devloop skips the project with a warning.
- Commit `.watched.json` in the project repo.

### Check your config

```bash
python3 validate_config.py [path]   # no path = .watched.json in the current folder
```

Devloop does not stop on a bad value: it quietly uses a default (`1h`, `General`, a generic
goal), so run this check after editing `.watched.json`. It is stricter than Devloop on
purpose: it only accepts the exact forms in the table above (`BL`, not `bl`).

## 3. The Telegram bot

Send **`/start`** to the bot once. It explains how Devloop works and adds three buttons
under the chat that stay there:

| Button | What it does |
| --- | --- |
| 📂 Projects | Your projects. Tap one to open its card. |
| 📥 Queue | The ideas you kept for later, with ▶️ Build all now. |
| ❓ Help | The short guide again. |

**A project card** shows the watcher, the builder and how often new ideas come. Its buttons:

- **⏸ Pause / ▶️ Turn on**: whether Devloop works on the project.
- **🔍 Find an idea now**: an idea within a few minutes, without waiting. If none comes, the
  bot says why.
- **👁 Watcher** (finds ideas) and **🔨 Builder** (writes the code): each opens a menu with
  🧠 Model (⚡ Haiku, ⚖️ Sonnet, 🧠 Opus, or the default) and 🎚 Effort (Low to Max).
- **⏱ How often**: every 10 min, 30 min, hour, 4 hours, or once a day.

Which value wins: **the idea card**, then **Telegram**, then **`.watched.json`**, then
**`.env`**. "Default" gives control back to the file. Only your Telegram account can use
the bot. The settings live in n8n: **n8n → Overview → Data tables → `devloop_projects`**.

```bash
devloop projects --all --remote   # ● = on, ○ = off (reads n8n)
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

Each idea card has three rows:

| Button | What it does | Same from the terminal |
| --- | --- | --- |
| ✅ Approve | Built within 2 minutes. You get a message when it is done. | `devloop approve <task-id>` |
| ❌ Reject | Closed. The next idea will be a different one. | `devloop reject <task-id>` |
| ✏️ Feedback | The bot asks for your notes. Reply to its message, then pick ✅ Approve with these notes, 🔁 Rewrite the idea, or 💾 Just keep them. | — |
| 📥 Later | Kept in the queue. It does not block new ideas. 📥 Queue → ▶️ Build all builds them one after another. | `devloop queue <task-id>`, `devloop queue --run` |
| ⚙️ Builder | Model and effort for this idea only. Change them until the build starts. | — |

When a build ends you get:

| Card | Buttons | Same from the terminal |
| --- | --- | --- |
| 🎉 Built | 🚀 Merge into main · 👀 Keep the branch | `devloop merge <task-id>` |
| ⚠️ Couldn't finish | 🔄 Try again · 🗑 Drop it | `devloop retry <task-id>` |

After you press a button, the card says what happens next.

While Devloop works you see a silent message: **🔍 Looking for an idea**, **🔁 Rewriting
the idea** or **🔨 Building** (with the model and the start time). It goes away by itself
when the result card arrives.

### Run things now instead of waiting

```bash
devloop observe --repo my-app                   # ask for a proposal now (skips watch_freq)
devloop execute --task <task-id>                # build an approved task now
devloop loop                                    # one full cycle now
systemctl --user start devloop-observe.service  # one observe run now, in the background
```

## 5. The timers

| Timer | Every | What it does |
| --- | --- | --- |
| `devloop-observe.timer` | 10 min | Proposes tasks for idle projects. |
| `devloop-execute.timer` | 2 min | Builds approved tasks, then merges the ones you asked to merge. |

```bash
systemctl --user list-timers 'devloop-*'                     # when is the next run
journalctl --user -u devloop-observe -u devloop-execute -f   # watch the runs live
systemctl --user disable --now devloop-observe.timer devloop-execute.timer  # stop both
systemctl --user enable --now devloop-observe.timer devloop-execute.timer   # start both
```

## 6. Rules you can rely on

- **A human approves every task.** Devloop never approves its own work.
- **One open task per project.** While a task waits for your answer, is being built, or is
  finished but not merged, Devloop proposes nothing new for that project. It keeps working
  on the other projects. Merge, Reject or Keep Branch frees the project.
- **One job per project at a time.** A project lock stops observe and execute from working
  on the same project together.
- **No repeats.** The agent sees earlier proposals and their result, so it does not propose
  a rejected or built idea again.
- **Work happens on its own branch, in its own folder:** `devloop/<task-id>`, built in a
  separate git worktree. Your folder, your branch and your unsaved work are not touched.
- **Only a merge touches your folder.** If you have unsaved work then, it is put in
  `git stash` first.
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
| `DEVLOOP_OBSERVE_EFFORT` | Effort for proposals (`high` by default). |
| `DEVLOOP_EXECUTE_EFFORT` | Effort for writing the code. Empty = the CLI default. |
| `DEVLOOP_OBSERVE_TIMEOUT` | Seconds allowed for a proposal. |
| `DEVLOOP_EXECUTE_TIMEOUT` | Seconds allowed to write the code. |
| `DEVLOOP_DIRTY_POLICY` | Uncommitted work during a merge: `stash` (default), `abort` or `reset`. |
| `DEV_ROOT` | Folder scanned for projects. |

After editing `.env`, run `devloop doctor` to check the result.

## 8. When something looks wrong

| Problem | Fix |
| --- | --- |
| My project is not in `devloop projects` | Check `.watched.json` is one valid JSON object, then `devloop watch`. |
| It is listed but never gets proposals | It is off in n8n, a task of it is still open or unmerged (`devloop status --repo my-app`), or its `watch_freq` has not passed yet. |
| A task failed | `devloop show <task-id>` shows why. Then `devloop retry <task-id>` or Dismiss. |
| Task says "timed out" | The task was too big for the time limit. Split it, or raise `DEVLOOP_EXECUTE_TIMEOUT`. |
| No Telegram messages | `devloop doctor`, and look at the Telegram lines. |
| `devloop: command not found` | Link it: `ln -s ~/DEV/LAB/devloop/.venv/bin/devloop ~/.local/bin/devloop`. |
