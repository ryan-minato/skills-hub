# Review threads, reviews, and Copilot code review

Use the column (MCP or gh) chosen in "Choose your path"; `O/R` and `N`
come from "Identify the repository". Every write operation in this file
publishes text — the Pre-publish gate in SKILL.md applies before each one.

## Read review summaries

- MCP: the capability that reads a PR's reviews.
- gh: `gh api repos/O/R/pulls/N/reviews`

Each review carries an author (`user.login`), a `state` (`APPROVED`,
`CHANGES_REQUESTED`, `COMMENTED`, `PENDING`), and a summary `body`.

## Read inline review comments

- MCP: the capability that reads a PR's review comments.
- gh: `gh api repos/O/R/pulls/N/comments`

These are code-anchored comments (each has `path`, a line position, and a
diff hunk). Plain conversation comments are a different resource and live
under `repos/O/R/issues/N/comments` — do not look for them here.

## Identify Copilot's review

Copilot's reviews and inline comments are the ones whose author login is
`copilot-pull-request-reviewer[bot]` (user type `Bot`). To filter with gh,
append this to either `gh api` call above:

    --jq '.[] | select(.user.login=="copilot-pull-request-reviewer[bot]")'

## Reply in a review thread

Replies are publishing — run the Pre-publish gate first.

- MCP: the capability that replies to a PR review comment (takes the
  numeric id of the inline comment being replied to, and the body).
- gh: `gh api -X POST repos/O/R/pulls/N/comments/COMMENT_ID/replies -F body=@REPLY.md`
  (the `@` makes gh read the body from the file).

`COMMENT_ID` is the `id` field of the inline comment, taken from "Read
inline review comments" above.

## Submit your own review

Review bodies and inline comments are publishing — run the Pre-publish
gate first.

- MCP, review without inline comments: the review-authoring capability in
  its immediate-submit form — pass the event (`COMMENT`, `APPROVE`, or
  `REQUEST_CHANGES`) and the body in one call.
- MCP, review with inline comments (three steps, in order):
  1. Start a **pending** review with the review-authoring capability —
     pass no event; passing one submits immediately and step 2 fails.
  2. Add each inline comment to the pending review with the
     pending-comment capability: path, body, and whether it anchors to a
     line or the whole file (line and side as optional refinements).
  3. Submit the pending review with the event and the summary body.
- gh: `gh pr review N -R O/R --comment --body-file REVIEW.md` — replace
  `--comment` with `--approve` or `--request-changes` when that is the
  verdict the user asked for.

## Request a Copilot code review

- MCP: the capability that requests a Copilot review for a PR.
- gh (requires gh ≥ 2.88): `gh pr edit N -R O/R --add-reviewer @copilot`

Copilot code review must be enabled for the repository or organization.
If GitHub rejects the reviewer, tell the user instead of retrying — no
invocation variant will succeed until the feature is enabled.
