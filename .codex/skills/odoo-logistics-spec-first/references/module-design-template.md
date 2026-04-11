# Module Design Template

Use this template when creating or updating a module design doc, interface doc, or implementation note.

## 1. Background

- Why this module or change exists
- Which business pain or workflow it solves

## 2. Goal

- What outcome must be true after delivery
- What is inside scope
- What is outside scope

## 3. OBB

### Outcome

- Final user-facing and system-facing result

### Behavior

- Main business flow
- Inputs
- Outputs
- Business rules

### Boundary

- Edge cases
- Abnormal cases
- Compatibility rules
- Ownership boundaries

## 4. Module Position

- Upstream modules
- Downstream modules
- Odoo native objects used
- Self-owned objects

## 5. Core Objects

- Main models/tables
- Key fields
- Relationship to waybill, batch, order, vehicle, trace, evidence

## 6. APIs and Events

- RESTful API list
- Event list
- Request/response or payload summary
- Admin/mini/open separation if applicable

## 7. Data and Indexes

- Table design or model design
- High-frequency queries
- Required indexes
- Retention/archival if large-volume data is involved

## 8. Page or Interaction

- Main user path
- Page list or page sections
- Key feedback states

## 9. Risks

- Technical risks
- Data risks
- Collaboration risks
- Rollout risks

## 10. Validation

- Function validation
- Boundary validation
- Exception validation
- Regression validation

## 11. Deliverables

- Docs to update
- Code/module paths
- APIs or SQL to deliver
- Test or verification artifacts
