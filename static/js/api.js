const API_BASE =
    "/api/v1";


async function apiRequest(
    endpoint,
    options = {}
) {

    const token =
        localStorage.getItem(
            "access_token"
        );


    const headers = {

        "Content-Type":
            "application/json",

        ...(options.headers || {})

    };


    if (token) {

        headers[
            "Authorization"
        ] =
            `Bearer ${token}`;

    }


    const response =
        await fetch(
            `${API_BASE}${endpoint}`,
            {
                ...options,
                headers
            }
        );


    let data;

    try {

        data =
            await response.json();

    } catch {

        data = {

            status:
                "error",

            message:
                "Invalid server response"

        };

    }


    if (!response.ok) {

        throw new Error(
            data.message ||
            "Request failed"
        );

    }


    return data;
}
