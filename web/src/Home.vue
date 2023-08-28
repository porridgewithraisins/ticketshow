<script setup lang="ts">
import { name } from '@/auth';

</script>

<template>
    <section>
        <h1>Ticketshow</h1>
        <p>Hi {{ name }}!</p>
    </section>
</template>

<style scoped>
section {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 80vh;
}

h1 {
    font-size: 4rem;
}

p {
    font-size: larger;
}
</style>