<script setup lang="ts">
import { call } from '@/api';
import { ref, computed } from 'vue';
import { isLoggedIn } from '@/auth';


const id = Number(window.location.hash.split("/").at(-1));

const allocation = ref<any>();
const loading = ref(true);

async function getData() {
    const { data: [alloc] } = await call("get_allocations", { id });
    if (!alloc) return window.location.hash = "#/allocations";
    const venuePromise = call("get_venues", { id: alloc.venue_id }).then(res => res.data[0]);
    const showPromise = call("get_shows", { id: alloc.show_id }).then(res => res.data[0]);
    const filledStatusPromise = call("get_filled_status", { id: alloc.id }).then(res => res.data.filled)
    const pricePromise = call("get_price", { id: alloc.id }).then(res => res.data.price);
    const [venue, show] = await Promise.all([venuePromise, showPromise]);

    alloc.venue = venue;
    delete alloc.venue_id;

    alloc.show = show;
    delete alloc.show_id;

    loading.value = false;
    allocation.value = alloc;

    filledStatusPromise.then(filled => allocation.value.filled = filled);
    pricePromise.then(price => allocation.value.price = price);
}

getData();

const isBookable = computed(() => isLoggedIn
    && new Date(allocation.value.time).getTime() > Date.now()
    && allocation.value.filled < allocation.value.capacity
)

const bookingQuantity = ref(0);
const bookingPrice = computed(() => bookingQuantity.value * allocation.value.price)
const bookingStatus = ref("");

const book = async () => {
    const { data, error } = await call("book", {
        quantity: bookingQuantity.value,
        gross_price: bookingPrice.value,
        allocation_id: id
    });

    if (error) return bookingStatus.value = error;

    bookingStatus.value = "Booked successfully";

    window.setTimeout(() => {
        window.location.hash = "#/my-bookings/" + data.id;
    }, 2000);
}

</script>

<template>
    <div v-if="loading">Loading...</div>
    <div v-else>
        <span>{{ allocation.show.tags }}</span>
        <span>{{ allocation.venue.name }}</span>
        <span>{{ allocation.venue.city }}</span>
        <span>{{ allocation.show.name }}</span>
        <span>{{ allocation.show.image }}</span>
        <span>{{ allocation.filled }}/ {{ allocation.capacity }}</span>

        <form v-if="isBookable" @submit.prevent="book">
            <label for="quantity">Quantity</label>
            <input id="quantity" type="number" min="0" :max="allocation.capacity - allocation.filled"
                v-model="bookingQuantity" />
            <label for="price">Price</label>
            <input type="number" readonly v-model="bookingPrice" />
            <input type="submit" value="Book">
        </form>
        <p>{{ bookingStatus }}</p>
    </div>
</template>