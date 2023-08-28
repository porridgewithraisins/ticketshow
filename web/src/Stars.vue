<script setup lang="ts">
import { ref } from 'vue';

const { stars } = defineProps<{ stars?: number }>();
const emit = defineEmits(["chosenstars"]);

const chosenStars = ref(stars || 0);

const choose = (i: number) => emit('chosenstars', chosenStars.value = i);

</script>

<template>
    <span v-for="i in 5" :key="i">
        <span v-if="i <= chosenStars" @click="choose(i)">★</span>
        <span v-else @click="choose(i)">☆</span>
    </span>
</template>

<style scoped>
span {
    font-size: 1.3em;
    cursor: pointer;
}
</style>