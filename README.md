# monostat – Highly opinionated minimal status page

This is the status page we use for pretix ([status.pretix.eu](https://status.pretix.eu)).
It is tailor-made to our needs and might or might not be useful for others.

## Opinions

### No components

Unlike *any* other status page software out there, this one does not have "components" that  can be marked as down individually.
pretix does not have a microservice architecture where system components like the API or other functional parts have independent operational failures.
Instead, we have a monolithic application where failures usually either affect the whole system, or just one very specific area of functionality.
So we'd either end up with just one component, or with hundreds of them.
Hundreds of components are neither helpful to our operations team who needs to quickly assess an incident, nor is it useful to have users scroll through a very long list.

### React to monitoring events …

When our site goes down, we want the status page to reflect this as soon as possible such that customers know we are aware of the issue.
At the same time, we do not want "update the status page" to be the first thing on our on-call person's list, they should start looking into the actual issue first.
Therefore, as soon as our monitoring system alerts our staff, we also want the status page to show something.

### … but do not trust them

However, we don't trust our monitoring, as it sometimes yields false-positives.
Therefore, while we want the status page to *show* the status from our monitoring, we do want to handle it differently than a real "incident".
For example, we only want to alert subscribers of our status after a human has confirmed it to be an actual incident.

### Require as few clicks as possible

An ongoing incident is a stressful situation for a small team.
Our previous status page was not updated well enough, partly because it was too much effort.
Therefore, this approach optimizes for the simplest possible user flows we could think of.
To take this to an extreme, we did not even want to have some kind of extra login for updating the status.
Therefore, most of the backend actions of this software live somewhere we are logged in to already: Slack.

### As little code as possible

We already maintain a big piece of software, we don't want this to grow into another one.
Therefore, this integrates with a bunch of software that we already use:

- Slack
- OpsGenie
- Rapidmail