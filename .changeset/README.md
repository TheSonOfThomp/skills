# Changesets

Describe each user-facing change with `npm run changeset`, commit the generated
file, and run `npm run version` to bump `package.json` and update `CHANGELOG.md`.
This package is installed from git rather than published to npm, so there is no
`changeset publish` step; tag the release after versioning.
