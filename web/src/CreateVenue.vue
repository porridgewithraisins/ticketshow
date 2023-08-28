<script setup lang="ts">

import { call } from '@/api';
import { computed, ref } from 'vue';

const venue = ref({
    name: { entry: "", error: "" },
    description: { entry: "", error: "" },
    image: { entry: "", error: "" },
    city: { entry: "", error: "" },
    address: { entry: "", error: "" },
});

const entries = computed(() => {
    const toSend = {};
    for (const field in venue.value) {
        toSend[field] = venue.value[field].entry;
    }
    return toSend;
})

const submit = async () => {
    const { error } = await call("create_venue", entries.value);
    if (!error) return window.location.hash = "#/venues";

    for (const field in error) {
        venue[field][error] = error[field];
    }
}

</script>

<template>
    <form @submit.prevent="submit">
        <label for="name">Name:</label>
        <input type="text" id="name" v-model="venue.name.entry"><br>
        <p :value="venue.name.error" />

        <label for="description">Description:</label>
        <input type="text" id="description" v-model="venue.description.entry"><br>
        <p :value="venue.description.error" />

        <label for="image">Image:</label>
        <input type="text" id="image" v-model="venue.image.entry"><br>
        <p :value="venue.image.error" />

        <label for="city">City:</label>
        <input type="text" id="city" v-model="venue.city.entry"><br>
        <p :value="venue.city.error" />

        <label for="address">Address:</label>
        <input type="text" id="address" v-model="venue.address.entry"><br>
        <p :value="venue.address.error" />

        <input type="submit" value="Create">
    </form>
</template>