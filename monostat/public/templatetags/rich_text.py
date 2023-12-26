import urllib.parse

import bleach
import markdown
from bleach import DEFAULT_CALLBACKS
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from markdown.postprocessors import Postprocessor

register = template.Library()

ALLOWED_TAGS = [
    "a",
    "abbr",
    "acronym",
    "b",
    "br",
    "code",
    "em",
    "i",
    "strong",
    "span",
    "strike",
    "s",
    "blockquote",
    "li",
    "ol",
    "ul",
    "p",
    "table",
    "tbody",
    "thead",
    "tr",
    "td",
    "th",
    "div",
    "hr",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "pre",
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "class"],
    "abbr": ["title"],
    "acronym": ["title"],
    "table": ["width"],
    "td": ["width", "align"],
    "div": ["class"],
    "p": ["class"],
    "span": ["class", "title"],
    "ol": ["start"],
}

ALLOWED_PROTOCOLS = ["http", "https", "mailto", "tel"]


def abslink_callback(attrs, new=False):
    """
    Makes sure that all links will be absolute links and will be opened in a new page with no
    window.opener attribute.
    """
    if (None, "href") not in attrs:
        return attrs
    url = attrs.get((None, "href"), "/")
    if not url.startswith("mailto:") and not url.startswith("tel:"):
        attrs[None, "href"] = urllib.parse.urljoin(settings.SITE_URL, url)
        attrs[None, "target"] = "_blank"
        attrs[None, "rel"] = "noopener"
    return attrs


class CleanPostprocessor(Postprocessor):
    def __init__(self, tags, attributes, protocols, strip):
        self.tags = tags
        self.attributes = attributes
        self.protocols = protocols
        self.strip = strip
        super().__init__()

    def run(self, text):
        return bleach.clean(
            text,
            tags=self.tags,
            attributes=self.attributes,
            protocols=self.protocols,
            strip=self.strip,
        )


def markdown_compile(source):
    tags = ALLOWED_TAGS
    exts = [
        "markdown.extensions.sane_lists",
        "markdown.extensions.nl2br",
    ]
    return bleach.clean(
        markdown.markdown(source, extensions=exts),
        strip=False,
        tags=tags,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
    )


@register.filter
def rich_text(text: str, **kwargs):
    text = str(text)
    linker = bleach.Linker(
        callbacks=DEFAULT_CALLBACKS + [abslink_callback], parse_email=True
    )
    body_md = linker.linkify(markdown_compile(text))
    return mark_safe(body_md)
