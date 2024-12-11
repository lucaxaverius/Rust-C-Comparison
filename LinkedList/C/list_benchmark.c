#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/list.h>
#include <linux/slab.h>
#include <linux/ktime.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Luca Saverio Esposito");
MODULE_DESCRIPTION("ListHead Benchmark Module");

#define NUM_ELEMENTS 1000000
#define SEED 12345

struct list_item {
    int data;
    struct list_head list;
};

static LIST_HEAD(my_list);

/* Generate a reproducible random number */
static u32 next_pseudo_random32(u32 seed)
{
    return seed * 1664525 + 1013904223;
}

static void generate_random_numbers(u32 *array, size_t size, u32 seed)
{
    size_t i;
    for (i = 0; i < size; i++) {
        seed = next_pseudo_random32(seed);
        array[i] = seed;
    }
}


static void insert_front(int *data, size_t size)
{
    size_t i;
    struct list_item *item;
    for (i = 0; i < size; i++) {
        item = kmalloc(sizeof(*item), GFP_KERNEL);
        if (!item) {
            pr_err("Failed to allocate memory for list item\n");
            return;
        }
        item->data = data[i];
        list_add(&item->list, &my_list);
    }
}

static void insert_back(int *data, size_t size)
{
    size_t i;
    struct list_item *item;
    for (i = 0; i < size; i++) {
        item = kmalloc(sizeof(*item), GFP_KERNEL);
        if (!item) {
            pr_err("Failed to allocate memory for list item\n");
            return;
        }
        item->data = data[i];
        list_add_tail(&item->list, &my_list);
    }
}

static void remove_all(void)
{
    struct list_item *item, *tmp;
    list_for_each_entry_safe(item, tmp, &my_list, list) {
        list_del(&item->list);
        kfree(item);
    }
}

static int __init list_benchmark_init(void)
{
    int *random_numbers;
    ktime_t start, end;
    s64 elapsed_ns;

    pr_info("Starting list_head benchmark module...\n");

    /* Allocate memory for random numbers */
    random_numbers = kmalloc_array(NUM_ELEMENTS, sizeof(int), GFP_KERNEL);
    if (!random_numbers) {
        pr_err("Failed to allocate memory for random numbers\n");
        return -ENOMEM;
    }

    /* Generate random numbers */
    generate_random_numbers(random_numbers, NUM_ELEMENTS, SEED);

    /* Insert at front */
    start = ktime_get();
    insert_front(random_numbers, NUM_ELEMENTS);
    end = ktime_get();
    elapsed_ns = ktime_to_ns(ktime_sub(end, start));
    pr_info("Time to insert %d elements at front: %lld ns\n", NUM_ELEMENTS, elapsed_ns);

    /* Remove all elements */
    start = ktime_get();
    remove_all();
    end = ktime_get();
    elapsed_ns = ktime_to_ns(ktime_sub(end, start));
    pr_info("Time to remove all elements: %lld ns\n", elapsed_ns);

    /* Insert at back */
    start = ktime_get();
    insert_back(random_numbers, NUM_ELEMENTS);
    end = ktime_get();
    elapsed_ns = ktime_to_ns(ktime_sub(end, start));
    pr_info("Time to insert %d elements at back: %lld ns\n", NUM_ELEMENTS, elapsed_ns);

    /* Remove all elements */
    start = ktime_get();
    remove_all();
    end = ktime_get();
    elapsed_ns = ktime_to_ns(ktime_sub(end, start));
    pr_info("Time to remove all elements: %lld ns\n", elapsed_ns);

    /* Free random numbers */
    kfree(random_numbers);

    pr_info("Benchmark completed.\n");
    return 0;
}

static void __exit list_benchmark_exit(void)
{
    pr_info("Exiting list_head benchmark module.\n");
}

module_init(list_benchmark_init);
module_exit(list_benchmark_exit);
