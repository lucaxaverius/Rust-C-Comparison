#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/ktime.h>
#include <linux/mm.h>
#include <linux/highmem.h>
#include <linux/compiler_attributes.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Luca Saverio Esposito");
MODULE_DESCRIPTION("Single Page Allocation Benchmark Module");

// Define constants for benchmarking
#define NUM_ITERATIONS 5000000 // Number of iterations for the test
#define PAGE_SIZE_BYTES 4096   // Size of one page in bytes
#define COUNT 2

// Global variables for cumulative timings
static s64 allocate_time = 0;
static s64 write_time = 0;
static s64 read_time = 0;

// Function prototypes
/*
void allocate_page(struct page **page);
void write_page(struct page *page);
void read_page(struct page *page);
*/
void allocate_page(struct page **page) noinline;
void write_page(struct page *page) noinline;
void read_page(struct page *page, char* buffer) noinline;
void test_page_operations(void) noinline;
int page_benchmark_init(void) noinline;

EXPORT_SYMBOL(allocate_page);
EXPORT_SYMBOL(write_page);
EXPORT_SYMBOL(read_page);
EXPORT_SYMBOL(test_page_operations);
EXPORT_SYMBOL(page_benchmark_init);

int page_benchmark_init(void) {
    pr_info("C-Page-Benchmark: Starting single-page benchmark module...\n");
    pr_info("C-Page-Benchmark: Iteration number %d \n",COUNT);
    test_page_operations();
    pr_info("C-Page-Benchmark: Iteration number %d ended \n",COUNT);
    pr_info("C-Page-Benchmark: Module initialization complete\n");

    return 0;
}

static void __exit page_benchmark_exit(void) {
    pr_info("C-Page-Benchmark: Exiting single-page benchmark module.\n");
}

// Function to test page allocation, write, and read
void test_page_operations(void) {
    struct page *page = NULL;
    ktime_t start, end;
    s64 elapsed_ns;
    
    char *buffer = kzalloc(PAGE_SIZE, GFP_KERNEL);
    if (!buffer) {
        pr_err("Failed to allocate memory for buffer\n");
        return;
    }

    for (int i = 0; i < NUM_ITERATIONS; i++) {
        // Allocate the page
        start = ktime_get();
        allocate_page(&page);
        end = ktime_get();
        elapsed_ns = ktime_to_ns(ktime_sub(end, start));
        allocate_time += elapsed_ns;

        // Write to the page
        start = ktime_get();
        write_page(page);
        end = ktime_get();
        elapsed_ns = ktime_to_ns(ktime_sub(end, start));
        write_time += elapsed_ns;

        // Read from the page
        start = ktime_get();
        read_page(page,buffer);
        end = ktime_get();
        elapsed_ns = ktime_to_ns(ktime_sub(end, start));
        read_time += elapsed_ns;

        // Free the page
        if (page) {
            __free_page(page);
            page = NULL;
        }
    }
    kfree(buffer); // Free the memory after use
    pr_info("C-Page-Benchmark: Total time to allocate: %lld ms\n", ktime_to_ms(allocate_time));
    pr_info("C-Page-Benchmark: Total time to write: %lld ms\n", ktime_to_ms(write_time));
    pr_info("C-Page-Benchmark: Total time to read: %lld ms\n", ktime_to_ms(read_time));
}

// Function to allocate a single page
void allocate_page(struct page **page) {
    *page = alloc_page(GFP_KERNEL);
    if (!*page) {
        pr_err("C-Page-Benchmark: Failed to allocate page\n");
    }
}

// Function to write to a single page
void write_page(struct page *page) {
    void *page_addr;

    if (page) {
        page_addr = kmap(page);
        if (page_addr) {
            memset(page_addr, 0xAA, PAGE_SIZE_BYTES); // Write a pattern
            kunmap(page);
        }
    }
}

// Function to read from a single page
void read_page(struct page *page, char * buffer) {
    void *page_addr;

    if (page) {
        page_addr = kmap(page);
        if (page_addr) {
            memcpy(buffer, page_addr, PAGE_SIZE); // Read the entire page into buffer
            kunmap(page);
        }
    }
}

module_init(page_benchmark_init);
module_exit(page_benchmark_exit);
