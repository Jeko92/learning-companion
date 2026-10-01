from html.parser import HTMLParser

from pytest_django.asserts import assertContains, assertTemplateUsed


class _ElementText(HTMLParser):
    """Collect the text of the first element matching a tag or a data-testid."""

    def __init__(self, *, tag: str | None = None, testid: str | None = None) -> None:
        super().__init__()
        self.tag, self.testid = tag, testid
        self.text: str | None = None
        self._depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self._depth:
            self._depth += 1
        elif self.text is None and (
            tag == self.tag or ("data-testid", self.testid) in attrs
        ):
            self._depth, self.text = 1, ""

    def handle_endtag(self, tag: str) -> None:  # noqa: ARG002 - HTMLParser API
        if self._depth:
            self._depth -= 1

    def handle_data(self, data: str) -> None:
        if self._depth and self.text is not None:
            self.text += data


def _element_text(html: str, **match: str) -> str | None:
    parser = _ElementText(**match)
    parser.feed(html)
    return parser.text


def test_home_page_renders_base_and_home_templates(client):
    response = client.get("/")

    assert response.status_code == 200
    assertTemplateUsed(response, "base.html")
    assertTemplateUsed(response, "core/home.html")


def test_home_page_shows_title_and_tagline(client):
    response = client.get("/")
    html = response.content.decode()

    assert response.status_code == 200
    assert (_element_text(html, tag="h1") or "").strip() == "Learning Companion"
    tagline = _element_text(html, testid="tagline")
    assert tagline is not None, "tagline element missing"
    assert tagline.strip(), "tagline is empty"
    assert "\n" not in tagline.strip(), "tagline must be one line"


def test_base_layout_links_tailwind_stylesheet(client):
    response = client.get("/")

    assertContains(response, 'href="/static/css/dist/styles.css"', html=False)
