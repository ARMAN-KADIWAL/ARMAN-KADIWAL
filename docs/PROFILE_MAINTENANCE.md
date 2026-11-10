# Keeping the profile personal

**Theme:** studio notebook, not a neon tech template.

- Cover illustration: `assets/studio-notes.svg` (original, static and readable on GitHub)
- Accent animation: `assets/ink-accent.gif` (original, self-hosted)
- Typing intro: external [readme-typing-svg](https://github.com/DenverCoder1/readme-typing-svg) service; if unavailable the rest of the page remains readable
- Contribution trail: `.github/workflows/contribution-trail.yml`, which uses the real GitHub contribution grid

## Content choices

Feature projects that exist and explain what is demonstrated vs. not yet verified.
Do not invent success rates, badges, milestones, stars, followers, rankings, or production claims.

## Snake animation

The `output` branch is created on the first successful GitHub Actions run.
If the picture is unavailable, inspect the [workflow runs](https://github.com/ARMAN-KADIWAL/ARMAN-KADIWAL/actions/workflows/contribution-trail.yml) and verify that Actions have permission to write repository contents.

The workflow runs when its file is first pushed, on manual dispatch, and daily at 03:23 UTC. GitHub may delay or disable scheduled runs after long inactivity. The animation is collapsed to keep the profile focused on actual projects.

## Maintenance

Review featured projects quarterly. Pin repositories manually via "Customize your pins" in the GitHub profile UI. The public display name can be adjusted under GitHub Settings; it is not changed by this README.

The old field-notes cover is superseded by `studio-notes.svg` and remains in Git history.
