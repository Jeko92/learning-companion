import pytest
from pytest_django.asserts import assertTemplateUsed


@pytest.mark.django_db
def test_home_page_renders_base_and_home_templates(client):
    response = client.get("/")

    assert response.status_code == 200
    assertTemplateUsed(response, "base.html")
    assertTemplateUsed(response, "core/home.html")
