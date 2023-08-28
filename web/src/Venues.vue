<script setup lang="ts">
import { call } from '@/api';
import { ref } from 'vue';
import { isAdmin } from '@/auth';

const venues = ref<any[]>([]);

call("get_venues", {}).then(({ data }) => venues.value = data);

</script>

<template>
    <h1>Venues</h1>
    <a v-if="isAdmin" href="#/venues/create">Create</a>
    <p v-if="!venues.length">Loading...</p>
    <ul>
        <li v-for="venue in venues">
            <span>{{ venue.name }}</span>
            <span>{{ venue.image }}</span>
            <span>{{ venue.city }}</span>
            <a :href="`#/venues/${venue.id}`">View</a>
        </li>
    </ul>
</template>