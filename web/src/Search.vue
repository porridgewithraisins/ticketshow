<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { call } from '@/api';
import { debounce } from '@/util';

const cities = await fetch("cities.json").then(res => res.json());
const citySentinel = "hahahahahahaha";

const q = ref('');
const city = ref(citySentinel);
const venueResults = ref<any[]>([]);
const showResults = ref<any[]>([]);

const hasCityBeenChosen = computed(() => city.value && city.value !== citySentinel)

const search = debounce(() => {
    call("search", { q: q.value })
        .then(({ data: { venues, shows } }) => [venueResults.value, showResults.value] = [venues, shows])
        .then(() => {
            if (hasCityBeenChosen.value)
                venueResults.value = venueResults.value.filter(v => v.city === city.value);
        });
}, 250)

onMounted(() => {
    document.addEventListener('mousedown', e => {
        if (!document.querySelector("section[role='search']")?.contains(e.target as any)) {
            q.value = '';
        }
    })
})

const navigate = x => {
    window.location.hash = x;
    window.location.reload();
}

</script>

<template>
    <section role="search">
        <div class="inputs">
            <select v-model="city" placeholder="City">
                <option :value="citySentinel" selected>City</option>
                <option v-for="city in cities" :key="city" :value="city">{{ city }}</option>
            </select>
            <input type="text" v-model="q" @input="search" />
        </div>
        <div class="results" v-if="q && (venueResults.length || showResults.length)">
            <div class="venues" v-if="venueResults.length && q">
                <p>Venues</p>
                <ul>
                    <li v-for="venue in venueResults">
                        <button @click="navigate(`#/venues/${venue.id}`)">{{ venue.name }}</button>
                    </li>
                </ul>
            </div>
            <div class="shows" v-if="showResults.length && q">
                <p>Shows</p>
                <ul>
                    <li v-for="show in showResults">
                        <button @click="navigate(`#/shows/${show.id}`)">{{ show.name }}</button>
                    </li>
                </ul>
            </div>
        </div>
    </section>
</template>

<style scoped>
select {
    width: 5rem;
}

section[role='search'] {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

    position: relative;
}

.inputs {
    display: flex;
    justify-content: center;
    align-items: center;
}

.results {
    position: absolute;
    top: 2.12rem;
    left: 0;
    width: 16rem;
    background: white;
    padding: 1rem;
    border: 1px solid black;
}
</style>