<script setup lang="ts">
import { ref } from 'vue';
import { call } from '@/api';
import Stars from '@/Stars.vue';

const id = Number(window.location.hash.split("/").at(-1));
const booking = ref<any>(null);

const load = async () => {
    const { data: [_booking], error } = await call("my_bookings", { id });
    if (!_booking || error) return window.location.hash = "#/my-bookings";
    const { data: [allocation] } = await call("get_allocations", { id: _booking.allocation_id })
    const venuePromise = call("get_venues", { id: allocation.venue_id }).then(res => res.data[0]);
    const showPromise = call("get_shows", { id: allocation.show_id }).then(res => res.data[0]);

    const [venue, show] = await Promise.all([venuePromise, showPromise]);

    allocation.venue = venue;
    allocation.show = show;
    _booking.allocation = allocation;

    delete allocation.venue_id;
    delete allocation.show_id
    delete _booking.allocation_id

    booking.value = _booking;
}

load();

const submitReview = () => {
    call("upsert_review", {
        booking_id: booking.value.id,
        rating: booking.value.rating,
        review: booking.value.review
    }).then(() => window.location.reload());
}

const deleteReview = () => {
    call("delete_review", { id: booking.value.id }).then(() => window.location.reload());
}

</script>

<template>
    <div v-if="booking">
        <p>{{ booking }}</p>
        <Stars @chosenstars="i => booking.rating = i" :stars="booking.rating" />
        <textarea v-model="booking.review"></textarea>
        <button @click="submitReview">Submit</button>
        <button @click="deleteReview">Delete</button>
    </div>
</template>