# Devloop Project Starter

A ready-to-use template for projects watched by [Devloop](https://github.com/rachid-log/devloop),
plus a cheat sheet of every command you need.

Every 10 minutes Devloop looks at your idle projects. For each one, an AI agent proposes
improvements across **14 areas** of the product, not only the code: product, design,
business logic, growth, content, SEO, performance, security, reliability, testing,
accessibility, analytics, docs and tooling. Each idea is about one area. You approve or
reject it in Telegram. Approved work is written on its own branch, in its own folder, and it
is merged only when you ask.

```text
every 10 min:  watch -> observe -> (you approve)
every 2 min:   execute -> commit -> (you ask) -> merge
```

---

## 1. Add a new project

**Easiest: do nothing.** Every folder in `DEV_ROOT` (default `~/DEV`) shows up in Telegram
under 📂 Projects, paused. Open it, tap ▶️ Turn on, then ✏️ Goal. No `.watched.json` needed.

- A folder that only groups repos (like `LAB`) is not listed itself. Its git repos are.
- A folder with no git gets `git init` and a first commit at its **first build**, not before.
  Devloop refuses if the folder holds more than 200 MB or one file over 50 MB
  (`DEVLOOP_GIT_INIT_MAX_MB`, `DEVLOOP_GIT_INIT_MAX_FILE_MB`).
- `DEVLOOP_DISCOVER_ALL=0` in the Devloop `.env` turns this off: then only folders with a
  `.watched.json` are listed.

A `.watched.json` is still useful to set starting values in the repo. Two ways to add one:

**A. With the command (recommended)**

```bash
devloop init ~/DEV/my-app --goal "Get more people through the checkout"
devloop watch          # register it and sync it to n8n
devloop projects       # check it is in the list
```

Add `--git` if the folder is not a Git repo yet. Add `--domain SEO` to pin the project to one
area (see the list below).

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
  "goal": "Get more people to sign up and stay",
  "facets": [],
  "domains_per_cycle": 2,
  "watch_freq": "1h",
  "active": true,
  "observe_effort": "high"
}
```

| Field | What it means |
| --- | --- |
| `name` | Display name. Optional: the folder name is used if empty. |
| `goal` | What the agent should care about. Be specific: it shapes every proposal. A business goal ("more sign-ups") gives better ideas than "stability". |
| `facets` | Areas the watcher may look at. `[]` means all 14, balanced. Example: `["ux", "growth", "seo"]`. |
| `domains_per_cycle` | How many ideas one cycle brings, each from a different area: `1` to `5`. Default `1`. |
| `watch_freq` | Minimum time between two cycles: `10m`, `1h`, `1d`... |
| `active` | Start value only. After the first `devloop watch`, Telegram (`/projects`) decides. |
| `observe_model`, `observe_effort` | Optional. Model and effort that propose tasks for this project. |
| `execute_model`, `execute_effort` | Optional. Model and effort that write the code for this project. |

Effort is one of `low`, `medium`, `high`, `xhigh`, `max`. Empty optional fields use the
values in the Devloop `.env`.

The old `domain` field is ignored now. `facets` replaced it.

### The 14 areas

| Key | Area | The agent looks as… |
| --- | --- | --- |
| `product` | 🧩 Product & features | a product manager |
| `ux` | 🎨 Design & UX | a product designer |
| `bl` | ⚙️ Business logic | a domain expert |
| `growth` | 📈 Growth & marketing | a growth marketer |
| `content` | ✍️ Content & copy | a copywriter |
| `seo` | 🔎 SEO | an SEO specialist |
| `perf` | ⚡ Performance | a performance engineer |
| `security` | 🔐 Security | a security engineer |
| `reliability` | 🛟 Reliability | a site reliability engineer |
| `testing` | 🧪 Testing & QA | a QA engineer |
| `a11y` | ♿ Accessibility | an accessibility specialist |
| `analytics` | 📊 Analytics | a product analyst |
| `docs` | 📚 Docs | a technical writer |
| `devex` | 🛠 Tooling & CI | a platform engineer |

**How a cycle picks its areas:**

- It counts the areas of the project's last 20 ideas.
- It takes the areas used least. On a tie, it takes the one used longest ago.
- With `domains_per_cycle: 3`, the agent runs **3 times, one after another**. Each run is one
  area and one expert, with a fresh start, so one area does not colour the next.
- Each run already sees the ideas of the earlier runs, so ideas do not overlap.
- If an area has nothing worth doing (SEO for a command-line tool), the agent says so. That
  area is left alone for 7 days, and the next area on the list is tried instead.
- If the agent fails (timeout, bad answer), the cycle stops. It does not burn more runs.

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

Send **`/start`** to the bot once. It explains how Devloop works and adds four buttons
under the chat that stay there:

| Button | What it does |
| --- | --- |
| 📂 Projects | Your projects. Tap one to open its card. |
| 📋 Tasks | Every task, for all projects or one, by what it needs: 🙋 needs you, 🚀 to merge (with Merge and Keep right in the list), 🔨 in progress, ✅ done. Tap a task to bring its card to the bottom of the chat. |
| 📥 Queue | The ideas you kept for later. Tap one to leave it out (▫️) or put it back (✅). Then ▶️ Build the selected ones, or 🗑 Drop the left-out ones. ✅ Select all and ▫️ Leave all out do it for every idea. |
| ❓ Help | The short guide again. |

**The project list** has pages of 16. Projects that are on come first.

**A project card** shows the goal, the watcher, the builder, the areas and how often new ideas
come. Its buttons:

- **⏸ Pause / ▶️ Turn on**: whether Devloop works on the project.
- **🔍 Find an idea now**: a cycle within a few minutes, without waiting. If no idea comes, the
  bot says why, as a reply to the card that blocks it.
- **🎯 Areas**: how many ideas per cycle (1 to 5), and which of the 14 areas are on.
  **↩️ All areas, balanced** turns them all on again.
- **👁 Watcher** (finds ideas) and **🔨 Builder** (writes the code): each opens a menu with
  🧠 Model (⚡ Haiku, ⚖️ Sonnet, 🧠 Opus, or the default) and 🎚 Effort (Low to Max).
- **⏱ How often**: a new cycle every 10 min, 30 min, hour, 4 hours, or once a day.
- **💡 My idea**: pick an area (or 🎲 let the watcher decide), then reply with your idea. Within
  about 2 minutes the watcher reads the project and turns it into a full idea card. Refine it
  with ✏️ Feedback → 🔁 Rewrite as often as you like, then ✅ Approve it. It works on paused
  projects too.
- **✏️ Goal**: the bot asks for the goal. Reply to its message. It replaces the goal in
  `.watched.json`.

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

Each idea card shows its area (for example **📈 Growth & marketing**) and has four rows:

| Button | What it does | Same from the terminal |
| --- | --- | --- |
| ✅ Approve | Built within 2 minutes. You get a message when it is done. | `devloop approve <task-id>` |
| ❌ Reject | Closed. The next idea will be a different one. | `devloop reject <task-id>` |
| ✏️ Feedback | The bot asks for your notes. Reply to its message, then pick ✅ Approve with these notes, 🔁 Rewrite the idea, or 💾 Just keep them. | — |
| 📥 Later | Kept in the queue. It does not block new ideas. In 📥 Queue you pick which ones to build; they are built one after another. Left-out ideas stay in the queue. | `devloop queue <task-id>`, `devloop queue --run` (builds the selected ones) |
| ✖ Cancel | Closes the idea without a verdict: no "why?" question. The watcher stops waiting for your answer and moves on to new ideas. The closed card has 📥 Move it to the queue to bring it back. | — |
| 🔀 Idea from another area | Closes this idea and brings one from an area that is not open yet, within a few minutes. The new card replies to the old one. | — |
| ⚙️ Builder | Model and effort for this idea only. Change them until the build starts. | — |

When a build ends you get:

| Card | Buttons | Same from the terminal |
| --- | --- | --- |
| 🎉 Built | 🚀 Merge · 👀 Keep · 🗑 Delete · 🔗 See the changes on GitHub | `devloop merge <task-id>`, `devloop delete-branch <task-id>` |
| ⚠️ Couldn't finish | 🔄 Try again · 🗑 Drop it | `devloop retry <task-id>` |

While a task waits for its build, its card has **✖ Cancel the build**. While it builds, it has
**⏹ Stop the build**: the build stops within 15 seconds and its half-done work is thrown away.
Both close the task, so the watcher moves on to new ideas. The closed card has
**📥 Move it to the queue** if you change your mind.

**Why cancel matters:** the watcher proposes nothing new for a project while one of its ideas
waits for your answer. ✖ Cancel or 📥 Later frees it without judging the idea.

**🎬 Demo video.** When the idea's area shows on screen (design, product, growth, content,
accessibility, SEO) and the project is a web app, Devloop records a real demo: an agent starts
your app from the task branch, clicks through the change like a user, and Playwright records it.
A desktop part (1280×720) comes first, then a phone part (390×844, centred) when the change shows
on phones. **The 🎉 card is the video itself**: the summary and the steps are its caption, and
🚀 Merge, 👀 Keep, 🗑 Delete, 🔗 GitHub and **🎬 Feedback on the video** sit under it.

**🎬 Feedback on the video:** reply with what the video should show, skip or do better. Within
about 2 minutes the demo is recorded again from the same branch with your notes, and a new 🎉
card comes. Nothing is rebuilt. When a demo could not be recorded, the button reads 🎬 Try the
demo again.
It uses your `node_modules` and your dev env files (`.env`, `.env.local`, `.env.development*`),
never `.env.deploy` or `.env.production`. If the app can't start (a database, a login, missing
secrets), the 🎉 card says why instead of sending a video. `DEVLOOP_DEMO=0` turns demos off.

The 🎉 card also shows:

- **🔗 See the changes on GitHub:** after each build the branch is pushed, and the link opens
  GitHub's compare page (base branch ... task branch). Only for repos with a GitHub `origin`.
  `DEVLOOP_PUSH_BRANCHES=0` turns the push off.
- **💻 `devloop open <task-id>`:** tap to copy, run it in any terminal. It checks the branch out
  in its own review folder (`~/.config/devloop/review/`) and opens it in VS Code. Your project
  folder stays on its branch. Commits you make there go on the task branch, and 🚀 Merge takes
  them along. After a merge, it opens the project folder instead.

**What 👀 Keep does:** it closes the idea without merging. The branch stays, on your
computer and on GitHub. The project is free for new ideas again. The closed card keeps
🚀 Merge and 🗑 Delete, so you can still decide later.

**What 🗑 Delete does:** the card asks first (🗑 Yes, delete it, or ⬅ No, go back). Within about
2 minutes the laptop deletes the branch on your computer and on GitHub, with its review folder.
Main is not touched. The task closes, and 📥 Move it to the queue builds the idea again from
scratch if you want it back. The delete stops, and the card says why, when the review folder
has unsaved edits or the branch is checked out in one of your folders. Only `devloop/` task
branches can be deleted this way.

After you press a button, the card says what happens next.

**One card per task.** Each task lives in a single message that changes as the task moves:
💡 idea → ✅ approved → 🔨 building since 15:50 → 🎉 built → 🚀 merged (or ⚠️ couldn't finish,
with 🔄 Try again). No new message for each step. When the demo video is ready, the video takes
the card's place (Telegram can't add a video to a text message), with the same text and buttons.

- **📄 The idea** shows the full idea on the card; **⬅ Back** returns.
- **✏️ Feedback**: the bot asks for your notes; once you reply, the question and your reply are
  deleted and the notes show on the card, with ✅ Approve with these notes / 🔁 Rewrite /
  💾 Just keep them.
- Pressing a button on an older message of a task makes that message the task's card again.
- **📋 Tasks → tap a task** moves its card to the bottom of the chat.

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

- **Passing failures heal themselves.** Devloop reads the end of the agent's output:
  - **Claude quota used up:** the build is tried again when the quota resets (the time is read
    from Claude's message, else 30 minutes). Until then no idea, rewrite or build runs, so no
    run is wasted. You get one ⏳ message.
  - **Network problem:** the build is tried again 5 minutes later. 🌐 message.
  - **Laptop off or crash during a build:** the build starts again on the next run. 🔌 message.
  - Each build gets **2 automatic retries** (`DEVLOOP_AUTO_RETRIES`). After that, and for any
    other error (tests fail, bad code, time limit), you get ⚠️ with 🔄 Try again.
  - Retries and the quota pause live in `~/.config/devloop/retries.json` and `quota_pause.json`.
    Delete `quota_pause.json` to end a pause early.

- **A human approves every task.** Devloop never approves its own work.
- **One open cycle per project.** While any idea of the last cycle waits for your answer, is
  being built, or is finished but not merged, Devloop starts no new cycle for that project. It
  keeps working on the other projects. Merge, Reject or Keep Branch on every idea frees the
  project.
- **One branch per idea, built one at a time.** The ideas of a cycle are built one after
  another, never together. Each starts from your main branch as it is at that moment, so merge
  one before the next is built when they touch the same files. If two branches still clash, the
  merge stops with ⚠️ and nothing is pushed.
- **The builder stays in its area.** It is told to change only what its idea's area needs.
- **One job per project at a time.** A project lock stops observe and execute from working
  on the same project together.
- **No repeats.** The agent sees earlier proposals and their result, so it does not propose
  a rejected or built idea again.
- **Work happens on its own branch, in its own folder:** `devloop/<task-id>`, built in a
  separate git worktree. Your folder, your branch and your unsaved work are not touched.
- **Only a merge touches your folder, and it puts everything back.** Unsaved work and
  untracked files are set aside in `git stash` for the merge and restored right after, and you
  are back on the branch you were on. If they can't be restored by themselves, the log says so
  and they wait in `git stash list`.
- **A failed task leaves nothing behind.** If the agent fails, runs out of time
  (`DEVLOOP_EXECUTE_TIMEOUT`, 20 min here) or writes no code, the branch is deleted and you
  get a Telegram message with Retry and Dismiss.
- **No force-push, ever.** 🚀 Merge deletes the task branch, its review folder and its GitHub
  copy after the merge is pushed.

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
| My project is not in `devloop projects --all` | It must sit in `DEV_ROOT`, or be a git repo one level below a grouping folder. Then `devloop watch`. |
| It is listed but never gets proposals | It is off in n8n, a task of it is still open or unmerged (`devloop status --repo my-app`), or its `watch_freq` has not passed yet. |
| A task failed | `devloop show <task-id>` shows why. Then `devloop retry <task-id>` or Dismiss. |
| Task says "timed out" | The task was too big for the time limit. Split it, or raise `DEVLOOP_EXECUTE_TIMEOUT`. |
| No Telegram messages | `devloop doctor`, and look at the Telegram lines. |
| `devloop: command not found` | Link it: `ln -s ~/DEV/LAB/devloop/.venv/bin/devloop ~/.local/bin/devloop`. |
