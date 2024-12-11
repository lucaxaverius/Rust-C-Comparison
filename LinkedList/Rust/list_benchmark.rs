// linked_list_test.rs

// SPDX-License-Identifier: GPL-2.0

//! Linked List Test Module

use kernel::prelude::*;
use kernel::list::{List,ListArc};

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
}

impl MyData {
    fn new(value: u32) -> Self {
        Self {
            value,
            links: ListLinks::new(),
        }
    }
}

// Safety: Implement `ListItem` for `MyData`, enabling its use in a `List`.
unsafe impl ListItem<0> for MyData {
    fn links(&self) -> &ListLinks<0> {
        &self.links
    }
}

pub struct ListBenchmarkModule {
    list: List<MyData, 0>,
}

impl KernelModule for ListBenchmarkModule {
    fn init(_module: &'static ThisModule) -> Result<Self> {
        pr_info!("Initializing Rust linked list benchmark module...\n");

        let mut benchmark = Self {
            list: List::new(),
        };

        // Generate random numbers
        const NUM_ELEMENTS: usize = 1000000;
        const SEED: u32 = 12345;
        let mut seed = SEED;

        let random_numbers: Vec<u32> = (0..NUM_ELEMENTS)
            .map(|_| {
                seed = next_pseudo_random32(seed);
                seed
            })
            .collect();

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

impl Drop for MyRustModule {
    fn drop(&mut self) {
        pr_info!("Exiting Rust linked list benchmark module.\n");
    }
}

impl MyRustModule {
    fn insert_front(&mut self, data: &[u32]) {
        for &value in data {
            if let Ok(arc) = ListArc::new(MyData::new(value), Flags::ZERO) {
                self.list.push_front(arc);
            } else {
                pr_err!("Failed to allocate ListArc for value: {}\n", value);
            }
        }
    }

    fn insert_back(&mut self, data: &[u32]) {
        for &value in data {
            if let Ok(arc) = ListArc::new(MyData::new(value), Flags::ZERO) {
                self.list.push_back(arc);
            } else {
                pr_err!("Failed to allocate ListArc for value: {}\n", value);
            }
        }
    }

    fn remove_all(&mut self) {
        while let Some(_) = self.list.pop_front() {
            // Automatically drops the item when popped.
        }
    }
}

/// Linear congruential generator for pseudo-random u32 values.
fn next_pseudo_random32(seed: u32) -> u32 {
    seed.wrapping_mul(1664525).wrapping_add(1013904223)
}