<script setup lang="ts">
import { isLoggedIn, logout } from './auth';

</script>

<template>
    <nav>
        <a href="#/venues">Venues</a>
        <a href="#/shows">Shows</a>
        <a href="#/allocations">Tickets</a>
        <a href="#/my-bookings">My Bookings</a>
        <button v-if="isLoggedIn" @click="logout" role="link">Logout</button>
        <a v-if="!isLoggedIn" href="#/login">Login</a>
        <a v-if="!isLoggedIn" href="#/register">Register</a>
    </nav>
</template>

<style scoped>
nav {
    display: flex;
    justify-content: space-around;
    gap: 1rem;
}

button {
    all: unset;
    height: max-content;
    text-decoration: underline;
    cursor: pointer;
}
</style>