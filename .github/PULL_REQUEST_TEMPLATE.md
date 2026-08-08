## Branch

`feature/<name>`

## Task checklist

<!-- Paste the relevant section's checklist from README.md, checked off item by item. -->

## Commit summary

<!-- One line per commit, or a short summary of what changed and why. -->

## Test checklist

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] `pytest` is green for the whole suite

## Code review checklist

- [ ] No business logic in views/blueprints — they call a service and wrap the result in `ApiResponse`
- [ ] Schemas validate all request/response shapes (Marshmallow)
- [ ] Every endpoint returns `ApiResponse` (or `ApiResponse[PageResponse[T]]` for lists)
- [ ] Commits are atomic (one file per commit) and follow Conventional Commits
