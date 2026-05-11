from .auth import obtener_token


def test_login_ok(client, seed_data):
    headers = obtener_token(
        client,
        "test1@test.com",
        "123456"
    )

    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Bearer ")

