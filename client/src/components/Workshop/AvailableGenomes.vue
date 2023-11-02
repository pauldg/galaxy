<script setup lang="ts">
import { ref } from "vue";

import { useFilterObjectArray } from "@/composables/filter";
import { useGenomes } from "@/composables/genomes";

import DelayedInput from "@/components/Common/DelayedInput.vue";

const filter = ref("");

const { genomes } = useGenomes();
const filteredGenomes = useFilterObjectArray(genomes, filter, [0, 1]);

const fields = [
    {
        key: 0,
        label: "name",
        sortable: true,
    },
    {
        key: 1,
        label: "desc",
        sortable: true,
    },
];

</script>

<template>
    <div>
        <h1>Genomes</h1>
        <p>
            All Genomes supported by this Galaxy instance. Hover over an item for more information. 
        </p>
        <DelayedInput placeholder="filter extensions" class="mb-3" :delay="200" @change="(val) => (filter = val)" />
        <b-table striped small sort-icon-left sort-by="extension" :items="filteredGenomes" :fields="fields">
            <template v-slot:cell(0)="row">
                    {{ row.item[0] }}
            </template>

            <template v-slot:cell(1)="row">
                {{ row.item[1] }}
            </template>
        </b-table>
    </div>
</template>

<style scoped>
table {
    cursor: default;
}
</style>
