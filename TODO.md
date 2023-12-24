# Roadmap

## MVP

- [x] Data model
  - [x] Incident
  - [x] IncidentUpdate
  - [x] OpsGenieAlert
  - [ ] Configuration
- [ ] Slack integration bootstrapping
- [ ] Django admin
- [ ] Page rendering
  - [ ] Current status
  - [ ] History
- [ ] OpsGenie incoming webhook → Slack message
  - [ ] deduplicate incidents
  - [ ] Slack option "add update"
  - [ ] Slack option "dismiss issue"
  - [ ] Slack option "close incident"
  - [ ] Ask in slack if incident should be resolved
  - [ ] Ask in slack in maintenance should be started
- [ ] Manually create incident from slack
- [ ] Create scheduled maintenance from slack
- [ ] Notify subscribers through rapidmail

## Later

- [ ] Allow to subscribe
- [ ] Widget for 500 pages
- [ ] Widget for pretix backend