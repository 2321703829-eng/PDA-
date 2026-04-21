# 2026-04-20 top navbar visual cleanup

## Goal

- fix the incorrect blue text on the system title and home entry inside the top navbar
- reduce the clutter on the right side of the navbar without changing any menu structure or behavior

## Completed

- added navbar-scoped color overrides so the brand, home entry, section entries, and dropdown text stay in the white navbar color system
- tightened the right-side systray into a grouped area with:
  - shared spacing
  - a divider from the main menu area
  - lighter pill-like button backgrounds
- refined company and user entry styling:
  - more compact width
  - cleaner company text presentation
  - subtler database badge inside the user menu trigger
  - better avatar weight

## Files

- `custom_addons/logistics_web/static/src/scss/logistics_web.scss`

## Verify

- the system title and `首页` should no longer appear blue in the navbar
- the right-side icon/company/user area should feel grouped and less noisy
