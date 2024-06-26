import { onMounted, readonly, ref } from "vue";

import { BrowsableFilesSourcePlugin, FilterFileSourcesOptions, getFileSources } from "@/api/remoteFiles";

/**
 * Composable for accessing and working with file sources.
 *
 * @param options - The options to filter the file sources.
 */
export function useFileSources(options: FilterFileSourcesOptions = {}) {
    const isLoading = ref(true);
    const hasWritable = ref(false);
    const fileSources = ref<BrowsableFilesSourcePlugin[]>([]);

    onMounted(async () => {
        fileSources.value = await getFileSources(options);
        hasWritable.value = fileSources.value.some((fs) => fs.writable);
        isLoading.value = false;
    });

    function getFileSourceById(id: string) {
        return fileSources.value.find((fs) => fs.id === id);
    }

    return {
        /**
         * The list of available file sources from the server.
         */
        fileSources: readonly(fileSources),
        /**
         * Whether the file sources are being loaded from the server.
         */
        isLoading: readonly(isLoading),
        /**
         * Whether the user can write files to any of the available file sources.
         */
        hasWritable: readonly(hasWritable),
        /**
         * Get the file source with the given ID.
         *
         * @param id - The ID of the file source to get.
         * @returns The file source with the given ID, if found.
         */
        getFileSourceById,
    };
}
