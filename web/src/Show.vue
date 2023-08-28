<script setup lang="ts">
import { call } from '@/api';
import { ref } from 'vue';
import AreYouSure from '@/AreYouSure.vue';
import { isAdmin } from '@/auth';

const id = Number(window.location.hash.split("/").at(-1));
const show = ref();


call("get_shows", { id }).then(({ data: [_show], error }) => {
    if (error || !_show) return window.location.hash = "#/shows";
    show.value = _show;
})

const showAreYouSure = ref(false);
const deleteStatusText = ref("");

const deleteShow = async () => {
    const { data, error } = await call("delete_show", { id });
    deleteStatusText.value = data === "success" ? "Deleted show successfully" : "Failed to delete show.";
}

const allocations = ref<any>([]);

call("get_allocations", { show_id: id }).then(({ data }) => allocations.value = data);

</script>

<template>
    {{ show }}
    <div v-if="allocations.length">
        {{ allocations.map(a => a.id) }}
    </div>
    <div v-if="isAdmin">
        <a :href="`$#/shows/edit/${id}`">Edit</a>
        <button @click="showAreYouSure = true">Delete</button>
        <AreYouSure v-if="showAreYouSure" @yes="deleteShow" @no="showAreYouSure = false" />
        <p v-if="deleteStatusText">{{ deleteStatusText }}</p>
    </div>
</template>