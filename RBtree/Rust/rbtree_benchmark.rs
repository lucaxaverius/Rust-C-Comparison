// SPDX-License-Identifier: GPL-2.0

//! RBTree Benchmark Module

use kernel::{
    prelude::*,
    rbtree::{RBTree, RBTreeNode},
    time::Ktime,
    alloc::{boxed::Box, flags},
};

module! {
    type: RBTreeBenchmarkModule,
    name: "rb_tree_benchmark",
    author: "Luca Saverio Esposito",
    description: "Benchmark for RBTree operations",
    license: "GPL",
}

struct RBTreeBenchmarkModule;

impl kernel::Module for RBTreeBenchmarkModule {
    fn init(_module: &'static ThisModule) -> Result<Self> {
        pr_info!("RBTree Benchmark Module init\n");

        // Number of elements for the benchmark
        const NUM_ELEMENTS: usize = 1000000;
        const SEED: u32 = 12345;

        // Generate random numbers
        let mut keys = generate_random_numbers(NUM_ELEMENTS, SEED)?;

        // Initialize an RBTree
        let mut tree = RBTree::new();

        // Measure time to insert all elements
        let start = Ktime::ktime_get();
        for &key in keys.iter() {
            tree.try_create_and_insert(key, key, flags::GFP_KERNEL)?;
        }
        let end = Ktime::ktime_get();
        let insert_time = (end - start).to_ns();
        pr_info!("Time to insert {} elements: {} ns\n", NUM_ELEMENTS, insert_time);

        // Measure time to find all elements and calculate average
        let mut total_find_time = 0;
        for &key in keys.iter() {
            let find_start = Ktime::ktime_get();
            tree.get(&key).expect("Key not found");
            let find_end = Ktime::ktime_get();
            total_find_time += (find_end - find_start).to_ns();
        }
        let avg_find_time = total_find_time / NUM_ELEMENTS as i64;
        pr_info!("Average time to find an element: {} ns\n", avg_find_time);

        // Measure time to remove all elements
        let start = Ktime::ktime_get();
        for &key in keys.iter() {
            tree.remove(&key);
        }
        let end = Ktime::ktime_get();
        let remove_time = (end - start).to_ns();
        pr_info!("Time to remove all elements: {} ns\n", remove_time);

        Ok(Self)
    }
}

impl Drop for RBTreeBenchmarkModule {
    fn drop(&mut self) {
        pr_info!("RBTree Benchmark Module exit\n");
    }
}

/// Generates random numbers using a simple LCG.
fn generate_random_numbers(num_elements: usize, seed: u32) -> Result<Vec<u32>> {
    let mut numbers = Vec::with_capacity(num_elements);
    let mut current = seed;

    for _ in 0..num_elements {
        current = next_pseudo_random32(current);
        numbers.push(current);
    }

    Ok(numbers)
}

/// Pseudo-random number generator using a linear congruential generator.
fn next_pseudo_random32(seed: u32) -> u32 {
    seed.wrapping_mul(1664525).wrapping_add(1013904223)
}
