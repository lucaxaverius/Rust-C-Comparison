#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/mutex.h>
#include <linux/ktime.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Luca Saverio Esposito");
MODULE_DESCRIPTION("Mutex Lock/Unlock Performance Test");

#define NUM_ITERATIONS 15000000
#define NUM_EXECUTION 30
#define COUNT 3

int mutex_benchmark_test(int count);
EXPORT_SYMBOL(mutex_benchmark_test);

static struct mutex test_mutex;

static int mutex_test_init(void)
{
    int ret;

    pr_info("C-Mutex-Benchmark: Initializing Mutex Lock/Unlock Performance Test...\n");

    pr_info("C-Mutex-Benchmark: Number of iterations: %d\n", COUNT);
    
    // Initialize the mutex
    mutex_init(&test_mutex);

    ret = mutex_benchmark_test(COUNT);

    pr_info("C-Mutex-Benchmark: Iteration %d-th ended\n", COUNT);
    pr_info("C-Mutex-Benchmark: Test module completed.\n");


    return ret;
}

int mutex_benchmark_test(int count){
    ktime_t start, end, lock_start, lock_end;
    s64 total_time_ms = 0, lock_time_ns = 0;
    s64 min_time_ns = LLONG_MAX, max_time_ns = 0;
    s64 elapsed_ns;
    int i;

    // Record start time
    start = ktime_get();

    for (i = 0; i < NUM_ITERATIONS; i++) {
        // Measure the time for lock/unlock cycle
        lock_start = ktime_get();
        mutex_lock(&test_mutex);
        mutex_unlock(&test_mutex);
        lock_end = ktime_get();

        elapsed_ns = ktime_to_ns(ktime_sub(lock_end, lock_start));
        lock_time_ns += elapsed_ns;

        // Update min and max times
        if (elapsed_ns < min_time_ns)
            min_time_ns = elapsed_ns;
        if (elapsed_ns > max_time_ns)
            max_time_ns = elapsed_ns;
    }

    // Record end time
    end = ktime_get();
    total_time_ms = ktime_to_ms(ktime_sub(end, start));

    // Log results
    pr_info("C-Mutex-Benchmark: Mutex Test %d Completed\n", count);
    pr_info("C-Mutex-Benchmark: Total time: %lld ms\n", total_time_ms);
    pr_info("C-Mutex-Benchmark: Total lock/unlock time: %lld ms\n", ktime_to_ms(lock_time_ns));
    pr_info("C-Mutex-Benchmark: Average time per lock/unlock: %lld ns\n", lock_time_ns / NUM_ITERATIONS);
    pr_info("C-Mutex-Benchmark: Minimum time per lock/unlock: %lld ns\n", min_time_ns);
    pr_info("C-Mutex-Benchmark: Maximum time per lock/unlock: %lld ns\n", max_time_ns);

    return 0;
}

static void __exit mutex_test_exit(void)
{
    pr_info("C-Mutex-Benchmark: Exiting Mutex Lock/Unlock Performance Test.\n");
}

module_init(mutex_test_init);
module_exit(mutex_test_exit);
