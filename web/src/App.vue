<script setup lang="ts">
import { ref, computed } from 'vue';
import Home from '@/Home.vue';
import Login from './Login.vue';
import Register from './Register.vue';
import Venues from './Venues.vue';
import Shows from './Shows.vue';
import Allocations from './Allocations.vue';
import Venue from './Venue.vue';
import Show from './Show.vue';
import Allocation from './Allocation.vue';
import CreateVenue from './CreateVenue.vue';
import CreateShow from './CreateShow.vue';
import EditVenue from './EditVenue.vue';
import EditShow from './EditShow.vue';
import EditAllocation from './EditAllocation.vue';
import CreateAllocation from './CreateAllocation.vue';
import Search from './Search.vue';
import Bookings from './Bookings.vue';
import Booking from './Booking.vue';
import Nav from './Nav.vue';

const routes = {
    "/login": Login,
    "/register": Register,
    "/venues": Venues,
    "/shows": Shows,
    "/allocations": Allocations,
    "/venues/[0-9]+": Venue,
    "/shows/[0-9]+": Show,
    "/allocations/[0-9]+": Allocation,
    "/venues/create": CreateVenue,
    "/shows/create": CreateShow,
    "/allocations/create": CreateAllocation,
    "/venues/edit/[0-9+]": EditVenue,
    "/shows/edit/[0-9+]": EditShow,
    "/allocations/edit/[0-9+]": EditAllocation,
    "/my-bookings": Bookings,
    "/my-bookings/[0-9]+": Booking
}

const currentPath = ref(window.location.hash);

const currentView = computed(() => {
    const routeName = Object.keys(routes).find(route => new RegExp(`^${route}$`).test(currentPath.value.slice(1)));
    const component = routeName ? routes[routeName as keyof typeof routes] : Home;
    return component;
});


window.addEventListener("hashchange", () => currentPath.value = window.location.hash);

</script>

<template>
    <header>
        <Suspense>
            <Search />
        </Suspense>
        <Nav />
    </header>
    <hr>
    <main>
        <Suspense>
            <component :is="currentView" />
        </Suspense>
    </main>
</template>

<style scoped>
header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

hr {
    border: none;
    background: #333;
    height: 2px;
}

</style>

<style>
* {
    font-family: monospace;
    font-size: 1rem;
}
</style>