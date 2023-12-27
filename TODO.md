# Roadmap

## MVP

- [x] Data model
  - [x] Incident
  - [x] IncidentUpdate
  - [x] OpsGenieAlert
  - [x] Configuration
- [x] Django admin
- [x] Page rendering
  - [x] Current status
  - [x] History
  - [x] Incident detail page
  - [x] Markdown support
  - [x] Use user timezone
  - [x] Mobile style
  - [x] RSS/Atom
- [ ] Slack integration bootstrapping
- [ ] OpsGenie incoming webhook → Slack message
  - [ ] deduplicate incidents
  - [ ] Slack option "add update"
  - [ ] Slack option "dismiss issue"
  - [ ] Slack option "close incident"
  - [ ] Ask in slack if incident should be resolved
  - [ ] Ask in slack in maintenance should be started
- [ ] Manually create incident from slack
- [ ] Create scheduled maintenance from slack
- [ ] Notify subscribers through Rapidmail
- [x] Housekeeping
  - [x] django-compressor
  - [x] CSP

## Later

- [ ] Allow to subscribe
- [ ] Widget for 500 pages
- [ ] Widget for pretix backend
- [ ] Public API
- [ ] Tooltips on history page
- [ ] 404/401/500 page
