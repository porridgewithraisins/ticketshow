<script setup lang="ts">
import { ref } from 'vue';
import { call } from '@/api';

const bookings = ref<any[]>([]);


const load = async () => {
    const { data } = await call("my_bookings", {});
    const allocationPromises = data
        .map(datum => datum.allocation_id)
        .map(id => call("get_allocations", { id }).then(res => res.data[0]))

    const allocations = await Promise.all(allocationPromises);

    const venuesPromise = Promise.all(allocations.map(({ venue_id }) => call("get_venues", { id: venue_id }).then(res => res.data[0])));
    const showsPromise = Promise.all(allocations.map(({ show_id }) => call("get_shows", { id: show_id }).then(res => res.data[0])));

    const [venues, shows] = await Promise.all([venuesPromise, showsPromise]);

    for (let i = 0; i < data.length; i++) {
        allocations[i].venue = venues[i];
        delete allocations[i].venue_id;

        allocations[i].show = shows[i];
        delete allocations[i].show_id;

        data[i].allocation = allocations[i];
        delete data[i].allocation_id;
    }

    bookings.value = data
}

load();

</script>

<template>
    <ul v-if="bookings.length">
        <li v-for="booking in bookings">
            {{ booking }}
            <a :href="`#/my-bookings/${booking.id}`">View</a>
        </li>
    </ul>
</template>