<script setup lang="ts">

import { ref } from 'vue';
import { call } from '@/api';

const name = ref('');
const email = ref('');
const password = ref('');
const nameError = ref('');
const emailError = ref('');
const passwordError = ref('');

const submit = async () => {
    const { error } = await call("register",
        { name: name.value, email: email.value, password: password.value }
    );
    if (!error) {
        window.location.hash = "#/login";
    }
    if (error?.name) nameError.value = error.name;
    if (error?.email) emailError.value = error.email;
    if (error?.password) passwordError.value = error.password;
}


</script>

<template>
    <h1>Register</h1>

    <form @submit.prevent="submit">
        <label for="name">Name</label>
        <input id="name" type="text" v-model="name" />
        <label for="email">Email</label>
        <input id="email" type="email" v-model="email" />
        <p :value="emailError"></p>
        <label for="password">Password</label>
        <input id="password" type="password" v-model="password" />
        <p :value="passwordError"></p>
        <button type="submit">Register</button>
    </form>
</template>