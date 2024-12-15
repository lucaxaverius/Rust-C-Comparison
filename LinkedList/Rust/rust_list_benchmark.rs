// SPDX-License-Identifier: GPL-2.0

//! Linked List Test Module

use kernel::prelude::*;
use kernel::list::*;
use kernel::time::{Ktime, ktime_ms_delta};
use kernel::{impl_has_list_links, impl_list_item, impl_list_arc_safe};
use kernel::macros::pin_data;

module! {
    type: ListBenchmarkModule,
    name: "Rust_List_Benchmark",
    author: "Luca Saverio Esposito",
    description: "Benchmark module for linked list operations in Rust",
    license: "GPL",
}

/// Struct representing an item in the list.
#[pin_data]
struct MyData {
    value: u32,
    #[pin] // Marking the field for pinning.
    links: ListLinks<0>, // Links for list traversal.
    #[pin] // Marking the field for pinning.
    tracker: AtomicTracker<0>, // Tracking mechanism for `ListArc`.
}

impl MyData {
    /// Pin-initialization for `MyData`.
    fn pin_init(value: u32) -> impl PinInit<Self, kernel::error::Error> {
        try_pin_init!(Self {
            value,
            links <- ListLinks::new(), // Use `<-` for in-place initialization.
            tracker <- AtomicTracker::new(), // Use `<-` for in-place initialization.
        })
    }
}


// Declare that `MyData` has `ListLinks`.
impl_has_list_links! {
    impl HasListLinks<0> for MyData { self.links }
}

// Declare that `MyData` supports `ListArc`.
impl_list_arc_safe! {
    impl ListArcSafe<0> for MyData {
        tracked_by tracker: AtomicTracker<0>;
    }
}

// Declare that `MyData` is a valid `ListItem`.
impl_list_item! {
    impl ListItem<0> for MyData { using ListLinks; }
}

/// Benchmark module for linked list operations.
pub struct ListBenchmarkModule {
    list: List<MyData, 0>, // Linked list of `MyData`.
}

impl kernel::Module for ListBenchmarkModule {
    fn init(_module: &'static ThisModule) -> Result<Self> {
        pr_info!("Initializing Rust linked list benchmark module...\n");

        let mut benchmark = Self {
            list: List::new(),
        };

        // Generate random numbers.
        const NUM_ELEMENTS: usize = 1_000_000;
        const SEED: u32 = 12345;
        let mut seed = SEED;

        let mut random_numbers = Vec::<u32, kernel::alloc::allocator::KVmalloc>::with_capacity(NUM_ELEMENTS, GFP_KERNEL)
            .expect("Failed to allocate vector");

        for _ in 0..NUM_ELEMENTS {
            seed = next_pseudo_random32(seed);
            random_numbers.push(seed, GFP_KERNEL).expect("Failed to push to vector");
        }
        
        // Print first 5 numbers.
        ListBenchmarkModule::print_first_n(&random_numbers, 5);
        // Insert elements at the front of the list.
        let start = Ktime::ktime_get();
        benchmark.insert_front(&random_numbers);
        let elapsed = ktime_ms_delta(Ktime::ktime_get(), start);
        pr_info!(
            "Time to insert {} elements at front: {} ms\n",
            NUM_ELEMENTS,
            elapsed
        );

        // Remove all elements.
        let start = Ktime::ktime_get();
        benchmark.remove_all();
        let elapsed = ktime_ms_delta(Ktime::ktime_get(), start);
        pr_info!("Time to remove all elements: {} ms\n", elapsed);

        // Insert elements at the back of the list.
        let start = Ktime::ktime_get();
        benchmark.insert_back(&random_numbers);
        let elapsed = ktime_ms_delta(Ktime::ktime_get(), start);
        pr_info!(
            "Time to insert {} elements at back: {} ms\n",
            NUM_ELEMENTS,
            elapsed
        );

        // Remove all elements.
        let start = Ktime::ktime_get();
        benchmark.remove_all();
        let elapsed = ktime_ms_delta(Ktime::ktime_get(), start);
        pr_info!("Time to remove all elements: {} ms\n", elapsed);

        pr_info!("Benchmark completed.\n");

        Ok(benchmark)
    }
}

impl Drop for ListBenchmarkModule {
    fn drop(&mut self) {
        pr_info!("Exiting Rust linked list benchmark module.\n");
    }
}

impl ListBenchmarkModule {
    /// Print first n data generated
    fn print_first_n(data: &[u32], n: i32){
        for i in 0..n {
            let value = data.get(i as usize).expect("Value not found");
            pr_info!("The {}-th element is: {}",i+1, value);
        }
    }

    /// Insert elements at the front of the list.
    fn insert_front(&mut self, data: &[u32]) {
        for &value in data {
            if let Ok(arc) = ListArc::pin_init(MyData::pin_init(value), GFP_KERNEL) {
                self.list.push_front(arc);
            } else {
                pr_err!("Failed to allocate ListArc for value: {}\n", value);
            }
        }
    }

    /// Insert elements at the back of the list.
    fn insert_back(&mut self, data: &[u32]) {
        for &value in data {
            if let Ok(arc) = ListArc::pin_init(MyData::pin_init(value), GFP_KERNEL) {
                self.list.push_back(arc);
            } else {
                pr_err!("Failed to allocate ListArc for value: {}\n", value);
            }
        }
    }

    /// Remove all elements from the list.
    fn remove_all(&mut self) {
        while let Some(item) = self.list.pop_front() {
            drop(item); // Ensure the ListArc is properly released.
        }
    }
}

/// Linear congruential generator for pseudo-random u32 values.
fn next_pseudo_random32(seed: u32) -> u32 {
    seed.wrapping_mul(1664525).wrapping_add(1013904223)
}
