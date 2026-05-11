def obtener_token(client, email, password):
    response = client.post(
        "/api/auth/login",
        json={
            "email_us": email,
            "contrasena_us": password,
        },
    )
    assert response.status_code == 200, response.text

    # Accedes directamente a "access_token" porque el JSON de respuesta 
    # ya es el TokenResponse
    token = response.json()["access_token"] 

    return {
        "Authorization": f"Bearer {token}"
    }