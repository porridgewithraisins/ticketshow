import { ref } from "vue";
import { call } from "@/api";

export let isLoggedIn = ref(!!localStorage.getItem("token"));

export let isAdmin = false;

export let name = "Stranger";

if (localStorage.getItem("token")) {
    const { data } = await call("me", {});
    isAdmin = data.is_admin;
    name = data.name;
}

export function login(token: string) {
    localStorage.setItem("token", token);
    window.location.hash = "#/shows";
}

export function logout() {
    localStorage.removeItem("token");
    window.location.hash = "#/login";
}

window.addEventListener("storage", () => (isLoggedIn.value = !!localStorage.getItem("token")));
