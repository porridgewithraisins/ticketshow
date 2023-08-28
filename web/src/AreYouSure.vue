<script setup lang="ts">
const emit = defineEmits(["yes", "no"]);
</script>

<template>
    <p>Are you sure?</p>
    <button @click="emit('yes')">Yes</button>
    <button @click="emit('no')">No</button>
</template>