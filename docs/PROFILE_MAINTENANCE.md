# Keeping the profile personal

The profile uses a warm studio-notebook palette: paper, dark green ink, terracotta and sage. The original `studio-notes.svg` and `ink-accent.gif` remain in the repository as earlier artwork.

## Original motion assets

All twelve GIFs under `assets/motion/` are original, self-hosted graphics: eight designs and four narrower mobile layouts. They contain no remote requests, scripts, credentials or synthetic activity statistics.

| Asset | Motion |
| --- | --- |
| `hero.gif` | Staggered name lettering, moving ink color, a drawing underline and an illustrated build/test/improve loop |
| `intro.gif` | Three short typewriter messages |
| `ghostdock.gif` | A travelling marker around service nodes |
| `backup.gif` | An orbit around a database illustration |
| `python.gif` | A moving code-line marker |
| `android.gif` | A phone interaction illustration |
| `toolkit.gif` | An ink highlight across eight tools |
| `method.gif` | A marker connecting build, test, learn and repeat |

Each GIF loops and has a matching `-still.png`. The README uses `<picture>` to select the static image when the reader requests reduced motion. The opening GIF frames also contain complete, readable text. Name motion stays inside the cover image: GitHub's sidebar name and normal README text do not accept custom JavaScript or page-wide CSS animations.

The cover, introduction, toolkit and method strip switch to dedicated mobile artwork at viewport widths up to 700 pixels, so text does not simply shrink with the desktop design.

GitHub readers can control GIF playback under **Settings → Accessibility → Motion → Autoplay animated images**. See [GitHub's accessibility documentation](https://docs.github.com/en/account-and-profile/how-tos/account-settings/managing-accessibility-settings).

## Rebuild the artwork

Use Python 3.10 or newer, Pillow, and the Liberation fonts. On Ubuntu, the font package is `fonts-liberation`.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/requirements-profile.txt
python scripts/render_profile_motion.py
```

To render just one asset:

```bash
python scripts/render_profile_motion.py --only hero
```

If the fonts are installed elsewhere, set `PROFILE_FONT_DIR` to the directory containing the Liberation `.ttf` files. The script is deterministic, uses a shared palette to avoid color shimmer, and writes dimensions, frame counts, duration and file sizes to `assets/motion/manifest.json` on a full rebuild.

## Content choices

Feature projects that exist. Describe what is demonstrated and what remains unverified. Do not invent success rates, badges, milestones, stars, followers, rankings or production claims. The moving checklist and project illustrations are decorative process drawings, not live monitoring or benchmark results.

## Contribution snake

The existing `.github/workflows/contribution-trail.yml` generates `snake.svg` and `snake-dark.svg` from the real contribution calendar and publishes them to the `output` branch. The contribution section is now visible without expanding a disclosure.

The schedule is daily at 03:23 UTC, with manual dispatch also available. GitHub may delay scheduled runs or disable them after prolonged inactivity. Inspect the [workflow runs](https://github.com/ARMAN-KADIWAL/ARMAN-KADIWAL/actions/workflows/contribution-trail.yml) if the images stop updating.

## Maintenance

Review featured projects periodically. Pin repositories manually through **Customize your pins** in the GitHub profile UI. The public display name and avatar are separate account settings; updating this README changes the illustrated name inside the profile, not those account fields.
