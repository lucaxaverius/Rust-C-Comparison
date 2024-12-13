#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/rbtree.h>
#include <linux/ktime.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Luca Saverio Esposito");
MODULE_DESCRIPTION("RBTree Benchmark Module");

#define NUM_ELEMENTS 1000000
#define SEED 12345

struct rbtest_node {
    struct rb_node node;
    u32 key;
    u32 value;
};

static struct rb_root tree_root = RB_ROOT;

static inline u32 next_pseudo_random32(u32 seed)
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

// Just for debugging, print the first n elements generated
static void print_first_n(u32 *array, int n){
    for (int i =0; i < n; i++){
        pr_info("C-RBTree-Benchmark: The %d-th element is: %u", i+1, array[i]);
    }
}


/* Comparison function for rb_find_add */
static int rb_find_add_cmp(struct rb_node *new, const struct rb_node *node)
{
    struct rbtest_node *new_node = container_of(new, struct rbtest_node, node);
    struct rbtest_node *existing_node = container_of(node, struct rbtest_node, node);

    if (new_node->key < existing_node->key)
        return -1;
    else if (new_node->key > existing_node->key)
        return 1;
    else
        return 0;
}


/* Insert a node into the RBTree */
static int rbtree_insert(struct rb_root *root, u32 key, u32 value)
{
    struct rbtest_node *new_node = kmalloc(sizeof(*new_node), GFP_KERNEL);
    if (!new_node)
        return -ENOMEM;

    new_node->key = key;
    new_node->value = value;

    /* Try to find and add the node */
    struct rb_node *found_node = rb_find_add(&new_node->node, root, rb_find_add_cmp);

    if (found_node) {
        /* A node with the same key already exists */
        struct rbtest_node *existing_node = container_of(found_node, struct rbtest_node, node);

        /* Create a copy of the existing node */
        struct rbtest_node *previous_node = kmalloc(sizeof(*previous_node), GFP_KERNEL);
        if (!previous_node) {
            kfree(new_node); /* Free the newly allocated node */
            return -ENOMEM;
        }

        /* Copy the existing node's data */
        *previous_node = *existing_node;

        /* Update the existing node's value */
        existing_node->value = value;

        /* Free the newly allocated node (not needed anymore) */
        kfree(new_node);

        /* Indicate successful replacement */
        return 1;
    }

    /* Node was successfully added, return 0 */
    return 0;
}


/* Comparison function for rb_find */
static int rb_find_cmp(const void *key, const struct rb_node *node)
{
    struct rbtest_node *existing_node = container_of(node, struct rbtest_node, node);
    u32 search_key = *(const u32 *)key;

    if (search_key < existing_node->key)
        return -1;
    else if (search_key > existing_node->key)
        return 1;
    else
        return 0;
}


/* Search for a node in the RBTree */
static struct rbtest_node *rbtree_search(struct rb_root *root, u32 key)
{
    struct rb_node *found_node = rb_find(&key, root, rb_find_cmp);
    return found_node ? container_of(found_node, struct rbtest_node, node) : NULL;
}


/* Remove all nodes from the RBTree */
static void rbtree_clear(struct rb_root *root)
{
    struct rb_node *node;
    while ((node = rb_first(root))) {
        rb_erase(node, root);
        kfree(container_of(node, struct rbtest_node, node));
    }
}

static int __init rbtree_benchmark_init(void)
{
    u32 *keys;
    ktime_t start, end;
    s64 elapsed_ns;
    s64 elapsed_ms;
    size_t i;

    pr_info("C-RBTree-Benchmark: RBTree Benchmark Module init\n");

    /* Allocate memory for random keys */
    keys = kmalloc_array(NUM_ELEMENTS, sizeof(u32), GFP_KERNEL);
    if (!keys)
        return -ENOMEM;

    /* Generate random keys */
    generate_random_numbers(keys, NUM_ELEMENTS, SEED);

    /* Print first 5 number for debugging*/
    print_first_n(keys, 5);
    
    /* Benchmark insertion */
    start = ktime_get();
    for (i = 0; i < NUM_ELEMENTS; i++) {
        int ret = rbtree_insert(&tree_root, keys[i], keys[i]);
        if (ret < 0) {  // Check for errors only
            pr_err("C-RBTree-Benchmark: Failed to insert key %u (error: %d)\n", keys[i], ret);
            kfree(keys);
            return ret;
        }
        if (ret == 1) {
            pr_info("C-RBTree-Benchmark: Replaced existing node with key %u\n", keys[i]);
        }
    }
    end = ktime_get();
    elapsed_ms = ktime_to_ms(ktime_sub(end, start));
    pr_info("C-RBTree-Benchmark: Time to insert %lu elements: %lld ms\n", NUM_ELEMENTS, elapsed_ms);

    /* Benchmark search */
    start = ktime_get();
    for (i = 0; i < NUM_ELEMENTS; i++) {
        struct rbtest_node *node = rbtree_search(&tree_root, keys[i]);
        if (!node) {
            pr_err("C-RBTree-Benchmark: Search failed for key %u\n", keys[i]);
        } else if (node->key != keys[i]) {
            pr_err("C-RBTree-Benchmark: Key mismatch! Expected: %u, Found: %u\n", keys[i], node->key);
        }
    }
    end = ktime_get();
    elapsed_ns = ktime_to_ns(ktime_sub(end, start));
    pr_info("C-RBTree-Benchmark: Average time to find an element: %lld ns\n", elapsed_ns / NUM_ELEMENTS);

    /* Benchmark deletion */
    start = ktime_get();
    rbtree_clear(&tree_root);
    end = ktime_get();
    elapsed_ms = ktime_to_ms(ktime_sub(end, start));
    pr_info("C-RBTree-Benchmark: Time to delete all the elements: %lld ns\n", elapsed_ms);

    /* Free the key array */
    kfree(keys);

    return 0;
}

static void __exit rbtree_benchmark_exit(void)
{
    rbtree_clear(&tree_root);
    pr_info("C-RBTree-Benchmark: RBTree Benchmark Module exit\n");
}

module_init(rbtree_benchmark_init);
module_exit(rbtree_benchmark_exit);
