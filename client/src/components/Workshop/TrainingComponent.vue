<script setup lang="ts">
import { useCssVar } from "@vueuse/core";
import { computed, ref, watch } from "vue";

import { useCounter } from "./counter";

import GenomeList from "./GenomeList.vue"
import Heading from "@/components/Common/Heading.vue";

const counterA = useCounter();
const counterB = useCounter();

const rootDiv = ref<null | HTMLDivElement>(null);
const color = useCssVar("--our-color", rootDiv);

const total = computed(() => counterA.count.value + counterB.count.value);

watch(
    () => counterA.count.value,
    () => {
        console.log("Counter A was clicked")

        color.value = "blue";
    },
);


</script>
<template>
    <div ref="rootDiv" class="training-component">
        <Heading h2 :bold="total === 3" size="sm">My Heading</Heading>

        You've clicked {{ counterA.count.value }} times!
        <button class="mx-2" @click="counterA.increment">Count</button>

        You've clicked {{ counterB.count.value }} times!
        <button @click="counterB.increment">Count</button>

        Total clicks is {{ total }}

        <GenomeList :count="total"/>

    </div>
</template>

<style scoped lang="scss">
.training-component {
    --our-color: red;
    button {
        background-color: var(--our-color);
    }
}
</style>