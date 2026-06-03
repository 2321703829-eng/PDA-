# 2026-05-29 Kebi Public Homepage Redesign

## Scope

- `custom_addons/kebi_website_custom`

## Changes

- Added a public homepage controller for `/`, `/zh_CN`, and `/zh_CN/`.
- Added a full-screen Tianshu logistics landing page with a generated container-ship hero asset.
- Kept the existing custom login page and wired homepage CTA buttons to `/web/login?redirect=/web`.
- Added a matching signup page shell for `/web/signup` so the entry path does not fall back to the default Odoo visual style.
- Kept Odoo backend menus untouched.

## Follow-up Changes

- Changed the homepage title to `天枢科技物流系统`.
- Compressed the public homepage into a no-scroll desktop first screen and removed the lower decorative operation/route cards.
- Replaced homepage top navigation anchors with real solution detail pages:
  - `/solutions/warehouse`
  - `/solutions/dispatch`
  - `/solutions/trace`
- Added a custom mock registration route `/register` so the public registration entry no longer falls into the default Odoo signup or portal pages.
- Added a visible `返回首页` entry on login, registration, and password reset screens.
- Updated auth screens to use the same container-ship hero background style as the homepage.

## Follow-up Changes 2

- Added `kebi.registration.request` to persist public trial registration submissions.
- Added an admin-only `/register/requests` page for viewing submitted trial requests.
- Removed the visible mock test credentials from the registration success message.
- Added a `TS` favicon asset and wired it into public website pages, login pages, and the backend web layout.
- Fixed detail-page top spacing so the brand and login actions no longer sit against the top edge.
- Rebuilt the `/aboutus` page with the same logistics hero background and themed detail layout.

## Verification

- Parsed `views/website_templates.xml` as XML.
- Parsed updated Python controller files with `ast.parse`.

## Notes

- Runtime verification needs to be repeated after each kebi development deployment.
- The generated hero image is stored under `kebi_website_custom/static/src/img/tianshu-hero-ship.png`.
