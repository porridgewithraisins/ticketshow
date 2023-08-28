<script setup lang="ts">
import { call } from '@/api';
import { ref } from 'vue';
import { isAdmin } from '@/auth';
const shows = ref<any[]>([]);

call("get_shows", {}).then(({ data }) => shows.value = data);

</script>

<template>
    <h1>Shows</h1>
    <a v-if="isAdmin" href="#/shows/create">Create</a>
    <p v-if="!shows.length">Loading...</p>
    <ul>
        <li v-for="show in shows">
            <span>{{ show.name }}</span>
            <span>{{ show.image }}</span>
            <span>{{ show.tags }}</span>
            <a :href="`#/shows/${show.id}`">View</a>
        </li>
    </ul>
</template>