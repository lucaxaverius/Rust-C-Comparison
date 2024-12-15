// SPDX-License-Identifier: GPL-2.0

//! RBTree Benchmark Module

use kernel::{
    prelude::*,
    rbtree::{RBTree},
    time::Ktime,
    alloc::flags,
};

module! {
    type: RBTreeBenchmarkModule,
    name: "Rust_RBTree_Benchmark",
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
        let mut seed = SEED;

    
        // Generate random numbers
        let mut keys = Vec::<u32, kernel::alloc::allocator::KVmalloc>::with_capacity(NUM_ELEMENTS, GFP_KERNEL)
            .expect("Failed to allocate vector");

        for _ in 0..NUM_ELEMENTS {
            seed = next_pseudo_random32(seed);
            keys.push(seed, GFP_KERNEL).expect("Failed to push to vector");
        }
        
        // Initialize an RBTree
        let mut tree = RBTree::new();
        
        print_first_n(&keys,5);

        // Measure time to insert all elements
        let start = Ktime::ktime_get();
        for &key in keys.iter() {
            tree.try_create_and_insert(key, key, flags::GFP_KERNEL).expect("Failed during node allocation");
        }
        let end = Ktime::ktime_get();
        let insert_time_ms = (end - start).to_ms();
        pr_info!("Time to insert {} elements: {} ms\n", NUM_ELEMENTS, insert_time_ms);

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
        let remove_time_ms = (end - start).to_ms();
        pr_info!("Time to remove all elements: {} ms\n", remove_time_ms);

        Ok(Self)
    }
}

impl Drop for RBTreeBenchmarkModule {
    fn drop(&mut self) {
        pr_info!("RBTree Benchmark Module exit\n");
    }
}


/// Pseudo-random number generator using a linear congruential generator.
fn next_pseudo_random32(seed: u32) -> u32 {
    seed.wrapping_mul(1664525).wrapping_add(1013904223)
}


/// Function to print the first n generated number
fn print_first_n(data: &[u32], n: i32){
    for i in 0..n {
        let value = data.get(i as usize).expect("Value not found");
        pr_info!("The {}-th element is: {}",i+1, value);
    }
}
