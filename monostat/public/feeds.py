from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed

from monostat.core.models import Incident, SiteConfiguration
from monostat.public.templatetags.rich_text import rich_text


class RSSFeed(Feed):
    link = "/"
    description = "All recent incidents."

    @property
    def title(self):
        config = SiteConfiguration.get_solo()
        return config.system_name + " System Status"

    def items(self):
        return Incident.objects.exclude(
            status__in=(Incident.Status.SUSPECTED, Incident.Status.DISMISSED),
        ).order_by("-created")[:50]

    def item_title(self, incident: Incident):
        return incident.title

    def item_description(self, incident: Incident):
        return rich_text(incident.summary)

    def item_pubdate(self, incident: Incident):
        return incident.created

    def item_updateddate(self, incident: Incident):
        return incident.updated


class AtomFeed(RSSFeed):
    feed_type = Atom1Feed
    subtitle = RSSFeed.description
