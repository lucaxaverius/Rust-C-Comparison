#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/mutex.h>
#include <linux/workqueue.h>
#include <linux/slab.h>
#include <linux/ktime.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Luca Saverio Esposito");
MODULE_DESCRIPTION("Mutex Performance Test with Workqueue and Variable Increments");
MODULE_VERSION("1.0");

#define NUM_WORK_ITEMS 8
#define NUM_ITERATIONS 100000

struct shared_data {
    struct mutex lock;
    int value;
};

struct work_data {
    struct work_struct work;
    struct shared_data *shared;
    int id;
    ktime_t start_time;
    ktime_t end_time;
};

// Use the global system_long_wq workqueue
static struct workqueue_struct *test_wq = system_long_wq;

void simulate_delay(unsigned int delay)
{
    unsigned int i;
    volatile unsigned int temp = 0;

    for (i = 0; i < delay; i++)
        temp += i;
}

static void work_func(struct work_struct *work)
{
    struct work_data *data = container_of(work, struct work_data, work);
    int i, increment;

    data->start_time = ktime_get();

    // Determine increment based on thread ID
    if (data->id == 0)
        increment = 1;
    else if (data->id == 1)
        increment = 2;
    else
        increment = 3;

    for (i = 0; i < NUM_ITERATIONS; i++) {
        mutex_lock(&data->shared->lock);

        pr_info("Work item %d acquired mutex.\n", data->id);

        // Critical section: increment the shared variable
        data->shared->value += increment;

        pr_info("Work item %d incremented value to: %d \n", data->id, data->shared->value);

        mutex_unlock(&data->shared->lock);
        pr_info("Thread %d releasing mutex \n", data->id);
    }
    
    data->end_time = ktime_get();
    pr_info(    
        "Work item %d completed. \n Execution time: %lld ns\n",
        data->id,
        ktime_to_ns(ktime_sub(data->end_time, data->start_time))
    );
}

static int __init mutex_test_init(void)
{
    int i;
    ktime_t start_time, end_time;
    s64 elapsed_ns;

    pr_info("Initializing Mutex Performance Test with Workqueue...\n");

    // Allocate and initialize shared data
    struct shared_data *shared = kzalloc(sizeof(*shared), GFP_KERNEL);
    if (!shared)
        return -ENOMEM;

    mutex_init(&shared->lock);

    // Record start time
    start_time = ktime_get();

    // Initialize and queue work items
    for (i = 0; i < NUM_WORK_ITEMS; i++) {
        struct work_data *work_item = kzalloc(sizeof(*work_item), GFP_KERNEL);
        if (!work_item)
            continue;

        work_item->shared = shared;
        work_item->id = i;
        INIT_WORK(&work_item->work, work_func);

        queue_work(test_wq, &work_item->work);
    }

    // Record end time
    end_time = ktime_get();
    elapsed_ns = ktime_to_ns(ktime_sub(end_time, start_time));

    pr_info("Work items have been queued.\n");
    return 0;
}

static void __exit mutex_test_exit(void)
{
    pr_info("Exiting Mutex Performance Test with Workqueue.\n");
    pr_info("Final shared variable value: %d\n", shared->value);

    // Free shared data
    kfree(shared);
}

module_init(mutex_test_init);
module_exit(mutex_test_exit);