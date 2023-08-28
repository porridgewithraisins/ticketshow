<script setup lang="ts">
import { call } from '@/api';
import { ref } from 'vue';
import { isAdmin } from '@/auth';

const allocations = ref<any[]>([]);

async function getData() {
    const { data } = await call("get_allocations", {});
    const venuesPromise = Promise.all(data.map(({ venue_id }) => call("get_venues", { id: venue_id }).then(res => res.data[0])));
    const showsPromise = Promise.all(data.map(({ show_id }) => call("get_shows", { id: show_id }).then(res => res.data[0])));

    const [venues, shows] = await Promise.all([venuesPromise, showsPromise]);

    for (let i = 0; i < data.length; i++) {
        data[i].venue = venues[i];
        delete data[i].venue_id;

        data[i].show = shows[i];
        delete data[i].show_id;
    }

    allocations.value = data;
}

getData();

</script>

<template>
    <h1>Allocations</h1>
    <a v-if="isAdmin" href="#/allocations/create">Create</a>
    <p v-if="!allocations.length">Loading...</p>
    <ul>
        <li v-for="allocation in allocations">
            <span>{{ allocation.show.tags }}</span>
            <span>{{ allocation.venue.name }}</span>
            <span>{{ allocation.venue.city }}</span>
            <span>{{ allocation.show.name }}</span>
            <span>{{ allocation.show.image }}</span>
            <span>{{ allocation.filled }}/ {{ allocation.capacity }}</span>
            <a :href="`#/allocations/${allocation.id}`">View</a>
        </li>
    </ul>
</template>