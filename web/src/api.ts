export async function call(method: string, data: any) {
    const server: string = import.meta.env.VITE_SERVER_URI;

    const uri = server + "/" + method;

    const token = localStorage.getItem("token");
    if (token) data.token = token;

    const response = await fetch(uri, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });

    const parsed = await response.json();

    return parsed;
}
