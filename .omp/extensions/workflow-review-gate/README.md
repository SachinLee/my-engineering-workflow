# Workflow Review Gate

An OMP extension that prevents duplicate final reviews of the same Trellis task
and source snapshot. It does not replace `trellis-check`, and it permits a new
review when remediation changes the snapshot.

The installed extension writes only ephemeral state to
`.omp/.runtime/workflow-review-gate.json`. Trellis remains the owner of task
records and final evidence.

Snapshots cover the current Git repository, or all repositories found within
four directory levels when OMP starts from a multi-repository workspace root.
The snapshot includes each repository's `HEAD` (including unborn repositories),
staged changes, unstaged changes, and untracked files. Ignored files and
`.omp/.runtime/` state are excluded. A snapshot or ledger persistence failure
blocks review dispatch instead of silently disabling duplicate protection.

An `INVALID` final review can use exactly one replacement slot, and that
replacement prompt must contain `Review retry: invalid`.

Run `npm test` in this directory to exercise the policy without starting OMP.
