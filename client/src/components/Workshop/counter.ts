import { ref } from "vue";

type Tuple<T> = [ T, T ];

const a: Tuple<string> = [ "1", "2" ];
a

export function useCounter() {
    const count = ref(0);

    const increment = () => {
        count.value += 1;
    };
    return {
        count,
        increment
    };
}