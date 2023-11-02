import { FetchReturnType } from "openapi-typescript-fetch/dist/cjs/types";
import type { Ref } from "vue";
import { ref } from "vue";

import { fetcher } from "@/schema";

const genomesFetcher = fetcher.path("/api/genomes").method("get").create();
// const data = ref<Array<string[]>>([]);


// onMounted(async () => {
//     const response = await fetchGenomes({});
//     data.value = response.data;
// });

// const displayedGenomes = computed(()=> data.value.slice(0,props.count));


// export interface Genomes {
//     genome: string;
// }

/**
 * Fetches a detailed array of datatypes available on this galaxy instance.
 * Does not cache the result or use a store.
 */
export function useGenomes() {
    const genomesLoading = ref(true);
    const genomes: Ref<FetchReturnType<typeof genomesFetcher>> = ref([]); //<Array<string[]>>([]);

    async function getGenomes() {
        try {
            const baseGenomes =  await genomesFetcher({});

            // type BaseGenomes = Exclude<typeof baseGenomes.data, string[]>;

            genomes.value = baseGenomes.data

        } catch (e) {
            console.error("unable to fetch available genomes\n", e);
        } finally {
            genomesLoading.value = false;
        }
    }

    getGenomes();

    return { genomes, genomesLoading };
}
