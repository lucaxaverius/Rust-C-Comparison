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

const NUM_ELEMENTS: usize = 1_000_000;
const NUM_EXECUTION: usize = 50;

//const NUM_ELEMENTS: usize = 10;
//const NUM_EXECUTION: usize = 2;

impl kernel::Module for RBTreeBenchmarkModule {
    #[no_mangle]
    fn init(_module: &'static ThisModule) -> Result<Self> {
        // Number of elements for the benchmark
        let mut seed = 12345;

        pr_info!("RBTree Benchmark Module init\n");

        for i in 0..NUM_EXECUTION{
            RBTreeBenchmarkModule::rust_rbtree_test(seed,i as i32);
            seed = seed +1; 
        }
        Ok(Self)
    }
}

impl Drop for RBTreeBenchmarkModule {
    fn drop(&mut self) {
        pr_info!("RBTree Benchmark Module exit\n");
    }
}

impl RBTreeBenchmarkModule{
    #[no_mangle]
    #[inline(never)]
    /// Test function executed
    fn rust_rbtree_test(seed: u32, count: i32){

        let mut seed_in = seed;

        // Generate random numbers
        let mut keys = Vec::<u32, kernel::alloc::allocator::KVmalloc>::with_capacity(NUM_ELEMENTS, GFP_KERNEL)
            .expect("Failed to allocate vector");

        for _ in 0..NUM_ELEMENTS {
            seed_in = next_pseudo_random32(seed_in);
            keys.push(seed_in, GFP_KERNEL).expect("Failed to push to vector");
        }
        pr_info!("Starting {}-th rbtree test \n",count+1);

        // Initialize an RBTree
        let mut tree = RBTree::new();
        
        //print_first_n(&keys,5);

        // insert all the values
        Self::insert_values(&mut tree, &keys);

        // Increment values of all nodes
        Self::iterate_all(&mut tree);


        /*
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
        pr_info!("Time to lookup all the elements: {} ms\n", Ktime::from_raw(total_find_time).to_ms() );
        */ 

        // remove all the nodes
        Self::remove_all(&mut tree, &keys);

    }
    #[no_mangle]
    #[inline(never)]
    /// Function to increment values of all nodes in the RBTree
    fn iterate_all(tree: &mut RBTree<u32, u32>) {
        let start = Ktime::ktime_get();

        for (_, value) in tree.iter_mut() {
            //pr_info!("Value before: {}", value);
            *value += 1; // Increment the value by 1
            //pr_info!("Value after: {}", value);
        }
        let end = Ktime::ktime_get();
        let increment_time_ms = (end - start).to_ms();
        pr_info!("Time to iterate over the rbtree: {} ms\n", increment_time_ms);
    }

    #[no_mangle]
    #[inline(never)]
    /// Insert into the tree the passed values
    fn insert_values(tree: &mut RBTree<u32, u32>, keys: &Vec::<u32, kernel::alloc::allocator::KVmalloc>){
        // Measure time to insert all elements
        let start = Ktime::ktime_get();
        for &key in keys.iter() {
            tree.try_create_and_insert(key, key, flags::GFP_KERNEL).expect("Failed during node allocation");
        }
        let end = Ktime::ktime_get();
        let insert_time_ms = (end - start).to_ms();
        pr_info!("Time to insert {} elements: {} ms\n", NUM_ELEMENTS, insert_time_ms);
    }

    #[no_mangle]
    #[inline(never)]
    /// Remove from the tree al the values
    fn remove_all(tree: &mut RBTree<u32, u32>, keys: &Vec::<u32, kernel::alloc::allocator::KVmalloc>){
        // Measure time to remove all elements
        let start = Ktime::ktime_get();
        for &key in keys.iter() {
            tree.remove(&key);
        }
        let end = Ktime::ktime_get();
        let remove_time_ms = (end - start).to_ms();
        pr_info!("Time to remove all elements: {} ms\n", remove_time_ms);
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

