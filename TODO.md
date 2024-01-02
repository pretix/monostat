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
- [x] Slack integration bootstrapping
- [x] OpsGenie incoming webhook → Slack message
  - [x] deduplicate incidents
  - [x] Slack option "confirm incident"
  - [x] Slack option "add update"
  - [x] Slack option "dismiss issue"
  - [x] Slack option "close incident"
  - [x] Ask in slack if incident should be resolved if all alerts are closed
  - [x] Ask in slack if auto-closed incident should be mentioned
- [x] Manually create incident from slack
- [ ] Show message in slack dialogs that subscribers will be notified
- [ ] Notify subscribers through Rapidmail
- [ ] Update slack after change on admin page
- [ ] Notify subscribers after change on admin page
- [ ] Install guide incl. API keys
- [x] Housekeeping
  - [x] django-compressor
  - [x] CSP

## Later

- [ ] Allow to subscribe
- [ ] Widget for 500 pages
- [ ] Widget for pretix backend
- [ ] Public API
- [ ] Tooltips on history page
- [ ] Ask in slack if maintenance should be started if time is reached
- [x] Create scheduled maintenance from slack
- [x] 404/401/500 page
