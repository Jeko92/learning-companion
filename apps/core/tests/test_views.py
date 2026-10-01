import re

import pytest
from pytest_django.asserts import assertContains, assertTemplateUsed


@pytest.mark.django_db
def test_home_page_renders_base_and_home_templates(client):
    response = client.get("/")

    assert response.status_code == 200
    assertTemplateUsed(response, "base.html")
    assertTemplateUsed(response, "core/home.html")


def test_home_page_shows_title_and_tagline(client):
    response = client.get("/")

    assertContains(response, "<h1>Learning Companion</h1>", html=True)
    tagline = re.search(
        r'<p data-testid="tagline">(?P<text>[^<]*)</p>', response.content.decode()
    )
    assert tagline is not None, "tagline element missing"
    text = tagline["text"].strip()
    assert text, "tagline is empty"
    assert "\n" not in text, "tagline must be one line"


def test_base_layout_links_tailwind_stylesheet(client):
    response = client.get("/")

    assertContains(response, 'href="/static/css/dist/styles.css"', html=False)
