<script setup lang="ts">

import { call } from '@/api';
import { computed, ref } from 'vue';

const id = Number(window.location.hash.split("/").at(-1));

const allocation = ref({
    venue_id: { entry: 0, error: "" },
    show_id: { entry: 0, error: "" },
    time: { entry: new Date(), error: "" },
    capacity: { entry: 0, error: "" },
    base_price: { entry: .0, error: "" },
    max_multiplier: { entry: .0, error: "" },
});

const load = async () => {
    call("get_allocations", { id }).then(({ data: [_venue], error }) => {
        if (error || !_venue) return window.location.hash = "#/venues";
        for (const field in _venue) {
            if (field in allocation.value)
                allocation.value[field].entry = _venue[field];
        }
    })
}

load();

const entries = computed(() => {
    const toSend = {};
    for (const field in allocation.value) {
        toSend[field] = allocation.value[field].entry;
    }
    return toSend;
})

const submit = async () => {
    const { error } = await call("update_allocation", entries.value);
    if (!error) return window.location.hash = "#/allocations";

    for (const field in error) {
        allocation[field][error] = error[field];
    }
}

</script>

<template>
    <form @submit.prevent="submit">
        <label for="name">Venue: </label>
        <input type="number" id="venue" v-model="allocation.venue_id.entry"><br>
        <p :value="allocation.venue_id.error" />

        <label for="show">Show:</label>
        <input type="number" id="show" v-model="allocation.show_id.entry"><br>
        <p :value="allocation.show_id.error" />

        <label for="time">Time:</label>
        <input type="datetime-local" id="time" v-model="allocation.time.entry"><br>
        <p :value="allocation.time.error" />

        <label for="capacity">Capacity:</label>
        <input type="number" id="capacity" v-model="allocation.capacity.entry"><br>
        <p :value="allocation.capacity.error" />

        <label for="base-price">Base Price:</label>
        <input type="number" step="any" id="base-price" v-model="allocation.base_price.entry"><br>
        <p :value="allocation.base_price.error" />

        <label for="max-multiplier">Max multiplier:</label>
        <input type="number" step="any" id="max-multiplier" v-model="allocation.max_multiplier.entry"><br>
        <p :value="allocation.max_multiplier.error" />

        <input type="submit" value="Update">
    </form>
</template>