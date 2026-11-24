# Profile artwork

The cover is an animated pen plotter drawing my initials. The initials and their curved underline use one path for the ink, brass nib and carriage. A flexible cable follows the gantry. The nib indicator follows pen contact, and a diagonal copper highlight crosses the name. The README provides day and night covers, a narrower composition for phones and still posters for readers who prefer reduced motion.

## GhostDock replay

The replay uses the sequence number, elapsed seconds and state from each of the ten events in one simulated GhostDock incident. Each entry stays on screen for the same amount of time so events at the same timestamp remain visible. The clock printed on the image comes from the journal. The reduced-motion poster shows the final entry.

[Pinned source journal](https://github.com/ARMAN-KADIWAL/GhostDock/blob/62c1c6c57bd19d5c29d6a08061875d0d2092b5a2/docs/examples/simulated-recovery/events.jsonl) · [Local replay data](../assets/workbench/ghostdock-trace.json)

To show another incident, copy those three fields from a simulated journal in sequence order, update its source commit in the data file, then update the profile’s transcript and links. Both the replay and the GitHub-readable table refer to that same recording.

## Illustrated project previews

Each linked illustration has a wide layout, a phone layout and stills for reduced motion. The pictures interpret behavior from the linked code.

- The SQLite test changes order 1 by +0.50 in a 40-order fixture. The drawn fingerprints stand in for the table content hashes. [Restore test](https://github.com/ARMAN-KADIWAL/backup-automation/blob/bfd56bca604638ce340b5f53af5694843e454fed/tests/test_core.py#L40)
- The two TCP paths carry the server’s `time` and `stats` requests and their replies. Port 8888 is the lab default. [Lab 82 server](https://github.com/ARMAN-KADIWAL/python-deep-dive/blob/main/Lab%2082/multi_server.py)
- The Bounce Lab illustration shows a touch, gravity, impact squash and diminishing rebounds. The dotted path and outlines show the bubble’s positions over time. [Android drawing code](https://github.com/ARMAN-KADIWAL/extra_work_123hy/blob/main/android-bounce-lab/app/src/main/java/com/example/bouncelab/MainActivity.kt)

## Rendering

Use Python 3.10 or newer, Pillow and the Liberation fonts. On Ubuntu the font package is `fonts-liberation`. Set `PROFILE_FONT_DIR` if the font files live somewhere else.

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r scripts/requirements-profile.txt
python scripts/render_workbench.py
```

Use `python scripts/render_workbench.py --only cover-night` or `python scripts/render_workbench.py --only study-backup-mobile` for one animation, or add `--poster` to preview a still. The workbench renderer shares the drawing and GIF helpers in `scripts/render_profile_motion.py`. That older renderer also rebuilds the moving toolkit under `assets/motion/`.

## Contribution calendar

The existing workflow draws the snake from my public GitHub contribution calendar and publishes its light and dark versions on the `output` branch. The reduced-motion version links straight to GitHub’s calendar. The workflow is scheduled daily at 03:23 UTC and can also be run manually.

[Contribution workflow](https://github.com/ARMAN-KADIWAL/ARMAN-KADIWAL/actions/workflows/contribution-trail.yml)
