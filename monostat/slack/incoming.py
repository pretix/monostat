from monostat.slack.slack_app import app


@app.action("dismiss_incident")
def approve_request(ack, say):
    ack()
    say("Button press received 👍")
