export function debounce<F extends (...args: any[]) => any>(fn: F, timePeriod: number) {
    let timerId: number;

    return (...args: Parameters<F>) => {
        window.clearTimeout(timerId);

        timerId = window.setTimeout(() => {
            fn(...args);
        }, timePeriod);
    };
}
