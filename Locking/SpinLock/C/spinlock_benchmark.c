#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/spinlock.h>
#include <linux/ktime.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Luca Saverio Esposito");
MODULE_DESCRIPTION("SpinLock Lock/Unlock Performance Test");

#define NUM_ITERATIONS 100000

static spinlock_t test_spinlock;

static int __init spinlock_test_init(void)
{
    ktime_t start, end, lock_start, lock_end;
    s64 total_time_ns = 0, lock_time_ns = 0;
    s64 min_time_ns = LLONG_MAX, max_time_ns = 0;
    s64 elapsed_ns;
    int i;

    pr_info("Initializing spinlock Lock/Unlock Performance Test...\n");

    // Initialize the spinlock
    spinlock_init(&test_spinlock);

    // Record start time
    start = ktime_get();

    for (i = 0; i < NUM_ITERATIONS; i++) {
        // Measure the time for lock/unlock cycle
        lock_start = ktime_get();
        spinlock_lock(&test_spinlock);
        spinlock_unlock(&test_spinlock);
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
    total_time_ns = ktime_to_ns(ktime_sub(end, start));

    // Log results
    pr_info("spinlock Test Completed\n");
    pr_info("Total time: %lld ns\n", total_time_ns);
    pr_info("Total lock/unlock time: %lld ns\n", lock_time_ns);
    pr_info("Average time per lock/unlock: %lld ns\n", lock_time_ns / NUM_ITERATIONS);
    pr_info("Minimum time per lock/unlock: %lld ns\n", min_time_ns);
    pr_info("Maximum time per lock/unlock: %lld ns\n", max_time_ns);

    return 0;
}

static void __exit spinlock_test_exit(void)
{
    pr_info("Exiting spinlock Lock/Unlock Performance Test.\n");
}

module_init(spinlock_test_init);
module_exit(spinlock_test_exit);
