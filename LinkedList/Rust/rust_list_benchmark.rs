// SPDX-License-Identifier: GPL-2.0

//! Linked List Test Module

use kernel::prelude::*;
use kernel::list::*;
use kernel::time::{Ktime, ktime_ms_delta};
use kernel::{impl_has_list_links,impl_list_item,impl_list_arc_safe, pin_init};

module! {
    type: ListBenchmarkModule,
    name: "rust_list_benchmark",
    author: "Luca Saverio Esposito",
    description: "Benchmark module for linked list operations in Rust",
    license: "GPL",
}

struct MyData {
    value: u32,
    links: ListLinks<0>,
    tracker: AtomicTracker<0>, // Tracking mechanism for `ListArc`
}

impl MyData {
    // Pin initialization for `MyData`.
    fn pin_init(value: u32) -> impl PinInit<Self> {
        pin_init!(Self {
            value,
            links: ListLinks::new(),
            tracker: AtomicTracker::new(),
        })
    }
}

// Declare that `MyData` has a `ListLinks` field.
impl_has_list_links! {
    impl HasListLinks<0> for MyData { self.links }
}

// Declare that `MyData` supports `ListArc`.
impl_list_arc_safe! {
    impl ListArcSafe<0> for MyData {
        tracked_by tracker: AtomicTracker<0>;
    }
}

impl_list_item! {
    impl ListItem<0> for MyData { using ListLinks; }
}


pub struct ListBenchmarkModule {
    list: List<MyData, 0>,
}

impl kernel::Module for ListBenchmarkModule {
    fn init(_module: &'static ThisModule) -> Result<Self> {
        pr_info!("Initializing Rust linked list benchmark module...\n");

        let mut benchmark = Self {
            list: List::new(),
        };

        // Generate random numbers
        const NUM_ELEMENTS: usize = 1000000;
        const SEED: u32 = 12345;
        let mut seed = SEED;

        let mut random_numbers = Vec::<u32, kernel::alloc::allocator::Kmalloc>::with_capacity(NUM_ELEMENTS, GFP_KERNEL)
        .expect("Failed to allocate vector");
    
        for _ in 0..NUM_ELEMENTS {
            seed = next_pseudo_random32(seed);
            random_numbers.push(seed, GFP_KERNEL).expect("Failed to push to vector");
        }
        

        // Insert elements at the front of the list
        let start = Ktime::ktime_get();
        benchmark.insert_front(&random_numbers);
        let elapsed = ktime_ms_delta(Ktime::ktime_get(), start);
        pr_info!(
            "Time to insert {} elements at front: {} ms\n",
            NUM_ELEMENTS,
            elapsed
        );

        // Remove all elements
        let start = Ktime::ktime_get();
        benchmark.remove_all();
        let elapsed = ktime_ms_delta(Ktime::ktime_get(), start);
        pr_info!("Time to remove all elements: {} ms\n", elapsed);

        // Insert elements at the back of the list
        let start = Ktime::ktime_get();
        benchmark.insert_back(&random_numbers);
        let elapsed = ktime_ms_delta(Ktime::ktime_get(), start);
        pr_info!(
            "Time to insert {} elements at back: {} ms\n",
            NUM_ELEMENTS,
            elapsed
        );

        // Remove all elements
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
    fn insert_front(&mut self, data: &[u32]) {
        for &value in data {
            if let Ok(arc) = ListArc::pin_init(MyData::pin_init(value), GFP_KERNEL) {
                self.list.push_front(arc);
            } else {
                pr_err!("Failed to allocate ListArc for value: {}\n", value);
            }
        }
    }

    fn insert_back(&mut self, data: &[u32]) {
        for &value in data {
            if let Ok(arc) = ListArc::pin_init(MyData::pin_init(value), GFP_KERNEL) {
                self.list.push_back(arc);
            } else {
                pr_err!("Failed to allocate ListArc for value: {}\n", value);
            }
        }
    }

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