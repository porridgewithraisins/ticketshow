<script setup lang="ts">

import { call } from '@/api';
import { computed, ref } from 'vue';

const id = Number(window.location.hash.split("/").at(-1));

const show = ref({
    name: { entry: "", error: "" },
    description: { entry: "", error: "" },
    image: { entry: "", error: "" },
    tags: { entry: "", error: "" },
});

const load = async () => {
    call("get_shows", { id }).then(({ data: [_show], error }) => {
        if (error || !_show) return window.location.hash = "#/venues";
        for (const field in _show) {
            if (field in show.value)
                show.value[field].entry = _show[field];
        }
    })
}

load();

const entries = computed(() => {
    const toSend = {};
    for (const field in show.value) {
        toSend[field] = show.value[field].entry;
    }
    return toSend;
})

const submit = async () => {
    const { error } = await call("update_show", entries.value);
    if (!error) return window.location.hash = "#/shows";

    for (const field in error) {
        show[field][error] = error[field];
    }
}

</script>

<template>
    <form @submit.prevent="submit">
        <label for="name">Name:</label>
        <input type="text" id="name" v-model="show.name.entry"><br>
        <p :value="show.name.error" />

        <label for="description">Description:</label>
        <input type="text" id="description" v-model="show.description.entry"><br>
        <p :value="show.description.error" />

        <label for="image">Image:</label>
        <input type="text" id="image" v-model="show.image.entry"><br>
        <p :value="show.image.error" />

        <label for="city">Tags:</label>
        <input type="text" id="tags" v-model="show.tags.entry"><br>
        <p :value="show.tags.error" />

        <input type="submit" value="Update">
    </form>
</template>