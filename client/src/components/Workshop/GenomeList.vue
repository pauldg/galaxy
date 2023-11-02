<script setup lang="ts">
import { computed, onMounted,ref } from "vue";

import { fetcher } from "@/schema";

import Heading from "@/components/Common/Heading.vue"

const props = defineProps({
   count: {
       type: Number,
       default: 10,
   }
});


const fetchGenomes = fetcher.path("/api/genomes").method("get").create();
const data = ref<Array<string[]>>([]);

onMounted(async () => {
    const response = await fetchGenomes({});
    data.value = response.data;
});

const displayedGenomes = computed(()=> data.value.slice(0,props.count));

</script>

<template>
    <div>
        <Heading h1 separator>Our Genome List</Heading>
        <div v-for="(genomes, index) in displayedGenomes" :key="index">
            {{ genomes }}

        </div>
    </div>


</template>