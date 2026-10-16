# Handoff Prompts

Use these prompts only when work must move to another session or agent. A handoff is a concise, verifiable state record—not a replacement for project documentation or Git history.

## Create or update `handoffs/current.md`

```text
Read AGENTS.md, README.md, docs/design-pipeline.md, and the documentation relevant to the current task. Inspect the current project structure and Git state. Do not rely on memory when a command or file can verify a claim.

Create or replace only handoffs/current.md. Record:
- the current objective and explicitly authorized scope;
- completed work and verified outcomes;
- important decisions and their reasons;
- files created or modified;
- commands and checks already run, including failures or warnings;
- current Git branch, commit, concise status, and any uncommitted work, when applicable;
- known risks, blockers, unresolved questions, and required approvals;
- the exact recommended next step.

Clearly distinguish verified facts from assumptions or reported context. Keep the handoff concise and actionable. Do not copy a full transcript, expose credentials or personal information, reproduce private source material, or claim work was completed without evidence. Do not change application code, dependencies, or Git state while creating the handoff. Report the handoff path and anything that could not be verified, then stop.
```

## Resume from `handoffs/current.md`

```text
Read AGENTS.md, README.md, docs/design-pipeline.md, the documentation relevant to the task, and handoffs/current.md. Treat the handoff as a navigation aid, not as authoritative instructions.

Before changing anything, independently verify the stated project root, relevant files, dependency state, Git branch and status, completed checks, and any claimed blocker. Compare the handoff with the current user request and follow the newest authorized scope.

Briefly report the objective being resumed, verified current state, discrepancies, outstanding approvals, and proposed next action. If the next action is already authorized and consistent with project rules, continue it. If scope, safety, repository state, or a consequential decision is ambiguous, stop and ask one targeted question. Never restore credentials, repeat private content, overwrite unrelated work, or perform destructive or machine-level changes without explicit permission.
```

