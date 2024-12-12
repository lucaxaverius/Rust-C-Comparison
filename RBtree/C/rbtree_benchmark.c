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

/* Comparison function for rb_find */
static int rb_key_cmp(const void *key, const struct rb_node *node)
{
    struct rbtest_node *rb_node = container_of(node, struct rbtest_node, node);
    u32 node_key = rb_node->key;

    if (*(u32 *)key < node_key)
        return -1;
    else if (*(u32 *)key > node_key)
        return 1;
    else
        return 0;
}

/* Insert a node into the RBTree */
static struct rbtest_node *rbtree_insert(struct rb_root *root, u32 key, u32 value)
{
    struct rb_node **new = &(root->rb_node), *parent = NULL;

    /* Traverse the tree to find the insertion point or existing node */
    while (*new) {
        struct rbtest_node *this = container_of(*new, struct rbtest_node, node);
        parent = *new;

        if (key < this->key)
            new = &((*new)->rb_left);
        else if (key > this->key)
            new = &((*new)->rb_right);
        else {
            /* If a node with the same key exists, replace it and return the previous one*/
            struct rbtest_node *previous = kmalloc(sizeof(*node), GFP_KERNEL);
            if (!previous)
                return NULL;

            /* Copy the node data*/
            previous->key = this->key;
            previous->value = this->value;

            /* Updating the node value*/
            this->value = value;
            return previous;
        }
    }

    /* Allocate and initialize a new node */
    struct rbtest_node *node = kmalloc(sizeof(*node), GFP_KERNEL);
    if (!node)
        return NULL;

    node->key = key;
    node->value = value;

    /* Link the new node and rebalance the tree */
    rb_link_node(&node->node, parent, new);
    rb_insert_color(&node->node, root);

    return NULL;
}

/* Search for a node in the RBTree */
static struct rbtest_node *rbtree_search(struct rb_root *root, u32 key)
{
    struct rb_node *found_node = rb_find(&key, root, rb_key_cmp);
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
    size_t i;

    pr_info("RBTree Benchmark Module init\n");

    /* Allocate memory for random keys */
    keys = kmalloc_array(NUM_ELEMENTS, sizeof(u32), GFP_KERNEL);
    if (!keys)
        return -ENOMEM;

    /* Generate random keys */
    generate_random_numbers(keys, NUM_ELEMENTS, SEED);

    /* Benchmark insertion */
    start = ktime_get();
    for (i = 0; i < NUM_ELEMENTS; i++) {
        if (!rbtree_insert(&tree_root, keys[i], keys[i])) {
            pr_err("Failed to insert key %u\n", keys[i]);
            kfree(keys);
            return -ENOMEM;
        }
    }
    end = ktime_get();
    elapsed_ns = ktime_to_ns(ktime_sub(end, start));
    pr_info("Time to insert %lu elements: %lld ns\n", NUM_ELEMENTS, elapsed_ns);

    /* Benchmark search */
    start = ktime_get();
    for (i = 0; i < NUM_ELEMENTS; i++) {
        struct rbtest_node *node = rbtree_search(&tree_root, keys[i]);
        if (!node || node->key != keys[i]) {
            pr_err("Key %u not found\n", keys[i]);
            kfree(keys);
            return -ENOENT;
        }
    }
    end = ktime_get();
    elapsed_ns = ktime_to_ns(ktime_sub(end, start));
    pr_info("Average time to find an element: %lld ns\n", elapsed_ns / NUM_ELEMENTS);

    /* Benchmark deletion */
    start = ktime_get();
    rbtree_clear(&tree_root);
    end = ktime_get();
    elapsed_ns = ktime_to_ns(ktime_sub(end, start));
    pr_info("Time to delete all elements: %lld ns\n", elapsed_ns);

    /* Free the key array */
    kfree(keys);

    return 0;
}

static void __exit rbtree_benchmark_exit(void)
{
    rbtree_clear(&tree_root);
    pr_info("RBTree Benchmark Module exit\n");
}

module_init(rbtree_benchmark_init);
module_exit(rbtree_benchmark_exit);
