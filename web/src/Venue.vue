<script setup lang="ts">
import { call } from '@/api';
import { ref } from 'vue';
import AreYouSure from '@/AreYouSure.vue';
import { isAdmin } from '@/auth';

const id = Number(window.location.hash.split("/").at(-1));
const venue = ref();


call("get_venues", { id }).then(({ data, error }) => {
    if (error || !data.length) return window.location.hash = "#/venues";
    venue.value = data[0];
})

const showAreYouSure = ref(false);
const deleteStatusText = ref("");

const deleteVenue = async () => {
    const { data, error } = await call("delete_venue", { id });
    deleteStatusText.value = data === "success" ? "Deleted venue successfully" : "Failed to delete venue.";
}

const allocations = ref<any>([]);

call("get_allocations", { venue_id: id }).then(({ data }) => allocations.value = data);

const exportInProgress = ref(false);
const exportReady = ref(false);
const exportResult = ref();

const exportVenue = async () => {
    exportInProgress.value = true;
    const { data: { promise_id } } = await call("export_venue", { id });

    const poll = async () => {
        const { data } = await call("check_export_venue_status", { promise_id });
        if (!data?.ready) {
            window.setTimeout(poll, 1000);
            return;
        }

        exportResult.value = data.result;
        exportReady.value = true;
    };

    poll();
}

const downloadPerShowStats = () => {

    let tsv = "show\tlink\tpercentage_filled\n"
    for (const datum of exportResult.value.average_percentage_filled_per_allocation) {
        const show = datum.show_name.replaceAll("\t", "\\t").replaceAll("\n", "\\n");
        const percentageFilled = datum.percentage_filled;
        const link = window.location.origin + "/#/allocations/" + datum.allocation_id;

        tsv += `${show}\t${percentageFilled}\t${link}\n`;
    }

    const file = new File([tsv], `export-venue-${id}.tsv`, { type: "text/tsv" });

    const url = URL.createObjectURL(file);
    const link = document.createElement("a");
    link.href = url;
    link.download = file.name;
    document.body.appendChild(link);
    link.click();
}


</script>

<template>
    {{ venue }}
    <div v-if="allocations.length">
        {{ allocations.map(a => a.id) }}
    </div>
    <div v-if="isAdmin">
        <button @click="exportVenue">Export</button>
        <a :href="`$#/shows/edit/${id}`">Edit</a>
        <button @click="showAreYouSure = true">Delete</button>
        <AreYouSure v-if="showAreYouSure" @yes="deleteVenue" @no="showAreYouSure = false" />
        <p v-if="deleteStatusText">{{ deleteStatusText }}</p>

        <div class="export" v-if="exportInProgress">
            <p v-if="!exportReady">Exporting...Do not close the tab</p>
            <div v-else>
                <pre>{{ JSON.stringify(exportResult, null, 4) }}</pre>
                <button @click="downloadPerShowStats">Download per show stats</button>
            </div>
        </div>
    </div>
</template>