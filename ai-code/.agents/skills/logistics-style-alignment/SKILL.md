---
name: logistics-style-alignment
description: Use when designing or reviewing warehouse, logistics, or adjacent backend pages that should stay visually and structurally aligned with the existing logistics module. Apply when creating new WMS pages, execution pages, list/detail flows, action entry points, or interaction patterns in this project. Prefer existing logistics frontend pages as reference pages before proposing new layouts.
---

# logistics-style-alignment

## Purpose

Keep warehouse and logistics pages inside the same Odoo backend feeling like one system.

This skill is for design and implementation work where the page is new, but the style should not be new.

## Use when

- Designing `logistics_wms_*` pages
- Adjusting warehouse execution pages
- Reviewing whether a new page deviates from the logistics module style
- Choosing layout, button placement, section ordering, or page flow for warehouse pages

## Core standard

- Warehouse pages should default to the existing logistics module style.
- Reuse logistics information architecture, page rhythm, and interaction patterns before inventing a new warehouse-specific style.
- Differences should mainly appear in business objects and fields, not in overall layout language.
- When in doubt, first find the closest logistics reference page, then adapt it to warehouse business content.

## Required workflow

1. Identify the closest existing logistics reference page.
2. Reuse the same page tier when possible:
   - list page
   - detail page
   - execution page
3. Reuse the same structural rhythm when possible:
   - top context area
   - middle main work area
   - lower summary / log / related info area
4. Reuse the same interaction style when possible:
   - primary button placement
   - state badge style
   - search and filter rhythm
   - tabs, smart buttons, and drill-down flow
5. Only introduce a different layout when the warehouse task genuinely cannot fit the logistics reference pattern.

## Warehouse-specific rule

For warehouse execution pages, prefer the same overall style as logistics execution pages, while swapping in warehouse business content such as:

- inbound
- putaway
- inventory
- pick
- check

Recommended execution-page baseline:

- top: business context
- middle: main execution area
- bottom: progress, logs, related info

When a split layout is needed, prefer a master-detail style:

- left: pending items
- right: current action area

## Project references

Read these first when needed:

- `d:\\Desktop\\Odoo\\ai-code\\前端设计\\一期前端相关设计\\01_模块设计\\04_运输与调度\\运输与调度模块前端设计草案.md`
- `d:\\Desktop\\Odoo\\ai-code\\前端设计\\一期前端相关设计\\01_模块设计\\05_仓储管理\\仓储管理前端接入设计草案.md`
- `d:\\Desktop\\Odoo\\ai-code\\仓管模块设计\\00_导航与总纲\\仓管模块设计启动讨论稿.md`

## Review checklist

- Does the page feel like it belongs to the same backend as logistics pages?
- Is there a clear logistics reference page for this warehouse page?
- Are button positions and state presentation consistent with existing logistics pages?
- Did the design change business content more than visual language?
- Was a new pattern introduced only because the old one truly did not fit?
