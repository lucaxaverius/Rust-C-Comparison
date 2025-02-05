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
//#define NUM_EXECUTION 50

//#define NUM_ELEMENTS 10
//#define NUM_EXECUTION 2

#define SEED 12346
#define I 2

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

/*
// Just for debugging, print the first n elements generated
static void print_first_n(u32 *array, int n){
    for (int i =0; i < n; i++){
        pr_info("C-RBTree-Benchmark: The %d-th element is: %u", i+1, array[i]);
    }
}
*/

int rbtree_benchmark_test(int seed, int count);
EXPORT_SYMBOL(rbtree_benchmark_test);
int rbtree_benchmark_init(void);
EXPORT_SYMBOL(rbtree_benchmark_init);
/*
int rbtree_insert(struct rb_root *root, u32 key, u32 value);
EXPORT_SYMBOL(rbtree_insert);
*/

int insert_values(struct rb_root *root, u32 * keys, u32* values);
EXPORT_SYMBOL(insert_values);
void remove_all(struct rb_root *root);
EXPORT_SYMBOL(remove_all);
void iterate_all(struct rb_root *root);
EXPORT_SYMBOL(iterate_all);


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


/* Insert or update a node in the RBTree 
int rbtree_insert(struct rb_root *root, u32 key, u32 value)
{
    struct rbtest_node *new_node = kmalloc(sizeof(*new_node), GFP_KERNEL);
    if (!new_node)
        return -ENOMEM;

    new_node->key = key;
    new_node->value = value;

    // Attempt to add the node to the RBTree 
    struct rb_node *found_node = rb_find_add(&new_node->node, root, rb_find_add_cmp);

    if (found_node) {
        // If a node already exists, just update its value 
        struct rbtest_node *existing_node = container_of(found_node, struct rbtest_node, node);
        existing_node->value = value;

        // Free the newly allocated node (no longer needed) 
        kfree(new_node);

        // Indicate that an existing node was updated 
        return 1;
    }

    // Node was successfully added, return 0 
    return 0;
}
*/

/* Insert or update all the nodes in the RBTree */
int insert_values(struct rb_root *root, u32 * keys, u32 * values){
    struct rbtest_node *new_node;
    for (int i=0; i<NUM_ELEMENTS; i++){
        new_node = kmalloc(sizeof(*new_node), GFP_KERNEL);
        if (!new_node)
            return -ENOMEM;

        new_node->key = keys[i];
        new_node->value = values[i];

        /* Attempt to add the node to the RBTree */
        struct rb_node *found_node = rb_find_add(&new_node->node, root, rb_find_add_cmp);

        if (found_node) {
            /* If a node already exists, just update its value */
            struct rbtest_node *existing_node = container_of(found_node, struct rbtest_node, node);
            existing_node->value = values[i];

            /* Free the newly allocated node (no longer needed) */
            kfree(new_node);

        }
    }
    return 0;
}


/* Comparison function for rb_find
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
 */
/* Search for a node in the RBTree 
static struct rbtest_node *rbtree_search(struct rb_root *root, u32 key)
{
    struct rb_node *found_node = rb_find(&key, root, rb_find_cmp);
    return found_node ? container_of(found_node, struct rbtest_node, node) : NULL;
}
*/

/* Remove all nodes from the RBTree */
void remove_all(struct rb_root *root)
{
    struct rb_node *node;
    while ((node = rb_first(root))) {
        rb_erase(node, root);
        kfree(container_of(node, struct rbtest_node, node));
    }
}

/* iterate over the tree*/
void iterate_all(struct rb_root *root) {
    struct rb_node *node;

    // Start from the first (smallest) node
    for (node = rb_first(root); node; node = rb_next(node)) {
        struct rbtest_node *rbtest_node = rb_entry(node, struct rbtest_node, node);
        
        //pr_info("C-RBTree-Benchmark: Value before: %u", rbtest_node->value);
        // Increment the value
        rbtest_node->value += 1;
        //pr_info("C-RBTree-Benchmark: Value after: %u", rbtest_node->value);
        //pr_info("C-RBTree-Benchmark: Incremented value to %u\n", rbtest_node->value);
    }
}


int rbtree_benchmark_test(int seed, int count){
    u32 *keys;
    ktime_t start, end;
    //s64 elapsed_ns;
    s64 elapsed_ms;

    pr_info("C-RBTree-Benchmark: Starting %d-th rbtree test \n",count);

    /* Allocate memory for random keys */
    keys = kvmalloc_array(NUM_ELEMENTS, sizeof(u32), GFP_KERNEL);
    if (!keys)
        return -ENOMEM;

    /* Generate random keys */
    generate_random_numbers(keys, NUM_ELEMENTS, seed);

    /* Print first 5 number for debugging*/
    //print_first_n(keys, 5);
    
    /* Benchmark insertion */
    start = ktime_get();
    int ret = insert_values(&tree_root, keys, keys);
    if (ret < 0) {  // Check for errors only
        pr_err("C-RBTree-Benchmark: Failed to insert key (error: %d)\n", ret);
        kvfree(keys);
        return ret;
    }
    end = ktime_get();
    elapsed_ms = ktime_to_ms(ktime_sub(end, start));
    pr_info("C-RBTree-Benchmark: Time to insert %lu elements: %lld ms\n", NUM_ELEMENTS, elapsed_ms);

    /*
    // Benchmark search 
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
    pr_info("C-RBTree-Benchmark: Time to lookup all the elements: %lld ms\n", ktime_to_ms(elapsed_ns) );
    */
    
    /* Increment values in the RBTree */
    start = ktime_get();
    iterate_all(&tree_root);
    end = ktime_get();
    elapsed_ms = ktime_to_ms(ktime_sub(end, start));
    pr_info("C-RBTree-Benchmark: Time to iterate over the rbtree: %lld ms\n", elapsed_ms);


    /* Benchmark deletion */
    start = ktime_get();
    remove_all(&tree_root);
    end = ktime_get();
    elapsed_ms = ktime_to_ms(ktime_sub(end, start));
    pr_info("C-RBTree-Benchmark: Time to delete all the elements: %lld ms\n", elapsed_ms);

    /* Free the key array */
    kvfree(keys);
    pr_info("C-RBTree-Benchmark: RBTree Benchmark %d completed\n",count);

    return 0;
}


int rbtree_benchmark_init(void)
{
    int ret;

    pr_info("C-RBTree-Benchmark: RBTree Benchmark Module init\n");

    ret = rbtree_benchmark_test(SEED,I);
    pr_info("C-RBTree-Benchmark: Module initialization complete\n");
    return ret;
}

static void __exit rbtree_benchmark_exit(void)
{
    remove_all(&tree_root);
    pr_info("C-RBTree-Benchmark: RBTree Benchmark Module exit\n");
}

module_init(rbtree_benchmark_init);
module_exit(rbtree_benchmark_exit);
