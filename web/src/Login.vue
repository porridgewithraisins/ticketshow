<script setup lang="ts">

import { ref } from 'vue';
import { call } from '@/api';
import { login } from './auth';

const email = ref('');
const password = ref('');
const emailError = ref('');
const passwordError = ref('');

const submit = async () => {
    const { data, error } = await call("login",
        { email: email.value, password: password.value }
    );
    if (!error) {
        login(data.token);
    }
    if (error?.email) emailError.value = error.email;
    if (error?.password) passwordError.value = error.password;
}


</script>

<template>
    <h1>Login</h1>

    <form @submit.prevent="submit">
        <label for="email">Email</label>
        <input id="email" type="email" v-model="email" />
        <p :value="emailError"></p>
        <label for="password">Password</label>
        <input id="password" type="password" v-model="password" />
        <p :value="passwordError"></p>
        <button type="submit">Login</button>
    </form>
</template>