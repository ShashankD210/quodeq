## Connect to CI

quodeq runs the same evaluation in a pipeline as on your machine, with the provider and model taken from the environment (*Command Line*, *Without the dashboard*). There are three ways to put its findings where a team reviews code: a pull request review posted from your own machine, a review posted by the pipeline itself, and a SARIF file uploaded to code scanning. Pull request reviews are GitHub only; SARIF works with GitHub and GitLab.

### Review a pull request from your machine

`quodeq review` detects the pull request for your current branch, evaluates only the files changed against the base branch, and posts the findings as a review through the `gh` CLI, so `gh` has to be installed and logged in.

| Key | Value |
| --- | --- |
| --pr | The pull request to post to. Without it, the one for the current branch. |
| --dimensions | A comma-separated subset, by name or alias: `sec`, `rel`, `mnt`, `perf`, `flex`, `ux`. All dimensions by default. |
| --time-limit | The total time budget in seconds. 300 by default. |
| --dry-run | Build the review without posting it. |
| --yes | Post without asking first. A run that is not interactive never asks. |

### Review it in the pipeline

Split the work in two steps: `quodeq evaluate --diff-from` analyzes the files the pull request changed, then `quodeq ci report` posts the result with the job's `GITHUB_TOKEN`. A run with `--diff-from` collects findings without scoring them, because grading part of a codebase would mislead, so the report reads them from the evidence with `--from-evidence`. It needs the run directory, which sits under the output directory, so locate it first. A minimal GitHub Actions job:

```yaml
permissions:
  pull-requests: write
  contents: read
steps:
  - uses: actions/checkout@v4
    with:
      fetch-depth: 0
  - run: pipx install quodeq
  - name: Evaluate the changed files
    env:
      AI_PROVIDER: openrouter
      AI_MODEL: anthropic/claude-sonnet-4
      OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
    run: quodeq evaluate . --diff-from "origin/${{ github.base_ref }}" --output "$RUNNER_TEMP/quodeq"
  - name: Post the review
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: |
      RUN_DIR=$(dirname "$(find "$RUNNER_TEMP/quodeq" -path '*/evidence' -type d | head -1)")
      quodeq ci report --evaluation-dir "$RUN_DIR" --from-evidence \
        --owner "${{ github.repository_owner }}" --repo "${{ github.event.repository.name }}" \
        --pr "${{ github.event.pull_request.number }}"
```

`fetch-depth: 0` matters: without the base branch in the clone, `--diff-from` has nothing to compare against. Any provider works here; set `AI_PROVIDER`, `AI_MODEL` and its key the same way. `quodeq ci report` also takes `--baseline-dir`, a previous evaluation, to mark which findings are new and which were already there, plus `--duration` and `--artifact-url` to show how long the run took and where its files can be downloaded.

`quodeq ci report` exits with 1 only when it cannot post: no token, no evaluation directory, or a GitHub API error. Findings never fail the build on their own. The repository's own workflow, `.github/workflows/quodeq-review.yml`, is a complete example with a time budget and a self-hosted local model.

### Upload to code scanning

SARIF is the findings format GitHub code scanning and GitLab understand. Add `--sarif findings.sarif` to an evaluation, or convert a finished one afterwards with `quodeq export sarif --evaluation-dir <dir> -o findings.sarif`. On GitHub the upload is one more step:

```yaml
- run: quodeq evaluate . --sarif quodeq.sarif
- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: quodeq.sarif
```

The file is built from the scored reports, so it belongs to a full evaluation, for instance on every push to the main branch or on a schedule, and not to a `--diff-from` run, which scores nothing. Use `--min-severity` to drop findings below a severity. Code snippets stay out of the file unless you pass `--with-snippets`; with it they leave the machine when the file is uploaded.

> **Every command documents itself**
>
> `quodeq review --help`, `quodeq ci report --help` and `quodeq export sarif --help` print the full flag lists, including defaults.
