#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/list.h>
#include <linux/slab.h>
#include <linux/ktime.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Luca Saverio Esposito");
MODULE_DESCRIPTION("ListHead Benchmark Module");

#define NUM_ELEMENTS 15000000
#define NUM_EXECUTION 30
#define SEED 12347
#define I 3

int list_benchmark_test(int seed, int count);
int list_benchmark_init(void);
void insert_front(int *data, size_t size);
void insert_back(int *data, size_t size);
void remove_all(void);
void iterate_all(void);

EXPORT_SYMBOL(list_benchmark_test);
EXPORT_SYMBOL(list_benchmark_init);
EXPORT_SYMBOL(insert_front);
EXPORT_SYMBOL(insert_back);
EXPORT_SYMBOL(remove_all);
EXPORT_SYMBOL(iterate_all);



struct list_item {
    u32 data;
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

/*
// Just for debugging, print the first n elements generated
static void print_first_n(u32 *array, int n){
    for (int i =0; i < n; i++){
        pr_info("C-List-Benchmark: The %d-th element is: %u", i+1, array[i]);
    }
}
*/
void insert_front(int *data, size_t size)
{
    size_t i;
    struct list_item *item;
    for (i = 0; i < size; i++) {
        item = kmalloc(sizeof(*item), GFP_KERNEL);
        if (!item) {
            pr_err("C-List-Benchmark: Failed to allocate memory for list item\n");
            return;
        }
        item->data = data[i];
        list_add(&item->list, &my_list);
    }
}

void insert_back(int *data, size_t size)
{
    size_t i;
    struct list_item *item;
    for (i = 0; i < size; i++) {
        item = kmalloc(sizeof(*item), GFP_KERNEL);
        if (!item) {
            pr_err("C-List-Benchmark: Failed to allocate memory for list item\n");
            return;
        }
        item->data = data[i];
        list_add_tail(&item->list, &my_list);
    }
}

void remove_all(void)
{
    struct list_item *item, *tmp;
    list_for_each_entry_safe(item, tmp, &my_list, list) {
        list_del(&item->list);
        kfree(item);
    }
}

void iterate_all(void)
{
    struct list_item *item;
    u32 dummy;
    list_for_each_entry(item, &my_list, list) {
        item->data+=1;    
        dummy = item->data;
    }
}

int list_benchmark_test(int seed, int count)
{
    int *random_numbers;
    ktime_t start, end;
    s64 elapsed_ns;

    pr_info("C-List-Benchmark: Starting %d-th list_head benchmark module...\n", count);

    /* Allocate memory for random numbers */
    random_numbers = kvmalloc_array(NUM_ELEMENTS, sizeof(int), GFP_KERNEL);
    if (!random_numbers) {
        pr_err("C-List-Benchmark: Failed to allocate memory for random numbers\n");
        return -ENOMEM;
    }

    /* Generate random numbers */
    generate_random_numbers(random_numbers, NUM_ELEMENTS, seed);

    /* Print first 5 element in the list: */
    //print_first_n(random_numbers, 1);

    /* Insert at front */
    start = ktime_get();
    insert_front(random_numbers, NUM_ELEMENTS);
    end = ktime_get();
    elapsed_ns = ktime_to_ms(ktime_sub(end, start));
    pr_info("C-List-Benchmark: Time to insert %d elements at front: %lld ms\n", NUM_ELEMENTS, elapsed_ns);

    /* Iterate all*/
    /*start = ktime_get();
    iterate_all();
    end = ktime_get();
    elapsed_ns = ktime_to_ms(ktime_sub(end, start));
    pr_info("C-List-Benchmark: Time to iterate %d elements: %lld ms\n", NUM_ELEMENTS, elapsed_ns);
    */

    /* Remove all elements */
    /*
    start = ktime_get();
    remove_all();
    end = ktime_get();
    elapsed_ns = ktime_to_ms(ktime_sub(end, start));
    pr_info("C-List-Benchmark: Time to remove all elements: %lld ms\n", elapsed_ns);
    */
    
    /* Insert at back */
    start = ktime_get();
    insert_back(random_numbers, NUM_ELEMENTS);
    end = ktime_get();
    elapsed_ns = ktime_to_ms(ktime_sub(end, start));
    pr_info("C-List-Benchmark: Time to insert %d elements at back: %lld ms\n", NUM_ELEMENTS, elapsed_ns);

    /* Iterate all*/
    start = ktime_get();
    iterate_all();
    end = ktime_get();
    elapsed_ns = ktime_to_ms(ktime_sub(end, start));
    pr_info("C-List-Benchmark: Time to iterate %d elements: %lld ms\n", NUM_ELEMENTS, elapsed_ns);

    /* Remove all elements */
    start = ktime_get();
    remove_all();
    end = ktime_get();
    elapsed_ns = ktime_to_ms(ktime_sub(end, start));
    pr_info("C-List-Benchmark: Time to remove all elements: %lld ms\n", elapsed_ns);

    /* Free random numbers */
    kvfree(random_numbers);

    pr_info("C-List-Benchmark: Benchmark %d-th completed.\n", count );
    return 0;
}

int list_benchmark_init(void){
    int ret;
    ret = list_benchmark_test(SEED, I);
    pr_info("C-List-Benchmark: Module initialization complete.\n");

    return ret;
}


static void __exit list_benchmark_exit(void)
{
    pr_info("C-List-Benchmark: Exiting list_head benchmark module.\n");
}

module_init(list_benchmark_init);
module_exit(list_benchmark_exit);
