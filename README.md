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

## Setup

Requirements:

- Docker (or Python 3.12 with a virtual environment, if you do not like Docker)
- PostgreSQL database
- redis database
- Reverse proxy to terminate TLS connections

Build the docker image or pull it from ``pretix/monostat:main``. Run the docker container with a volume mounted to
``/data`` that is readable and writable for uid 15372 and port 80 exposed to a reverse proxy. You can and should set
the following environment variables:

- ``MONOSTAT_SITE_URL``: URL the site will be online at, e.g. ``https://pretixstatus.com``
- ``MONOSTAT_DB_TYPE``: Database type, e.g. ``postgresql``
- ``MONOSTAT_DB_NAME``: Database name
- ``MONOSTAT_DB_USER``: Database user
- ``MONOSTAT_DB_PASS``: Database password
- ``MONOSTAT_DB_HOST``: Database host
- ``MONOSTAT_DB_PORT``: Database port
- ``MONOSTAT_REDIS_HOST``: Redis host
- ``MONOSTAT_REDIS_PORT``: Redis port
- ``MONOSTAT_REDIS_PASSWORD``: Redis ``AUTH`` password
- ``MONOSTAT_MAIL_FROM``: Email address to use as sender for outgoing email
- ``MONOSTAT_MAIL_HOST``: SMTP server
- ``MONOSTAT_MAIL_PORT``: SMTP server port
- ``MONOSTAT_MAIL_TLS``/``MONOSTAT_MAIL_SSL``: Set to ``"True"`` to use STARTTLS or SSL on SMTP connections 
- ``MONOSTAT_MAIL_USER``: SMTP authentication username
- ``MONOSTAT_MAIL_PASSWORD``: SMTP authentication password
- ``NUM_WORKERS``: Number of processes/threads for both the web worker and the task worker. Defaults to the number of CPUs.

The database migrations will automatically run on startup unless you set the environment variable ``AUTOMIGRATE=skip``.
Create a first user:

    docker exec -it containername monostat createsuperuser

And log in at ``https://SITE_URL/admin/``. Then, set up the remaining settings:

1. Go to "Site Configuration" and adjust configuration as needed.
2. Go to "Notification Configuration" and adjust configuration as needed.
3. Go to "OpsGenie Configuration" and note down the webhook secret.
   1. Open OpsGenie
   2. Go to Integrations → Add integration → Webhook → Choose a name and team
   3. Create the integration
   4. Set the webhook URL to ``https://SITE_URL/integrations/opsgenie/hook/SECRET``
   5. Activate "Add Alert Description to Payload"
   6. Activate "Post to Webhook URL for Opsgenie alerts"
   7. Activate at least the Alert actions "Alert is created", "Alert is closed", "Alert description is updated",
      and "Alert message is updated".
   8. Set up alert filters if wanted.
   9. Turn on integration
4. Go to the [Slack developer page](https://api.slack.com/apps)
   1. Click "Create New App"
   2. Choose "From an app manifest", pick a workspace and paste in the manifest from the file ``slack-app.json``
      from this repository. Replace ``SITE_URL`` with your site's URL and create the app.
   3. Go to "Install App" to install the app to your workspace
   4. Note down the "Bot User OAuth Token"
   5. Go to "Basic Information", note down the "Signing Secret"
   6. Go to "Slack Configuration" in monostat admin, enter the bot token and signing secret as well as the
      name of an existing, public channel (e.g. ``#statuspage``).
5. Restart the docker container, as there is a known issue with caching of the slack secrets.
6. You should be good to go!