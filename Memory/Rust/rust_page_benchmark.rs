// SPDX-License-Identifier: GPL-2.0
//! Single Page Allocation Benchmark Module in Rust.

use kernel::prelude::*;
use kernel::page::Page;
use kernel::time::*;

module! {
    type: PageBenchmarkModule,
    name: "Rust_Page_Benchmark",
    author: "Luca Saverio Esposito",
    description: "Single Page Allocation Benchmark Module",
    license: "GPL",
}

struct PageBenchmarkModule;

impl kernel::Module for PageBenchmarkModule {
    fn init(_module: &'static ThisModule) -> Result<Self> {
        pr_info!("Starting single-page benchmark module...\n");
        test_page_operations();
        pr_info!("Iteration {} ended.\n", ITERATION);
        pr_info!("Module initialization complete.\n");
        Ok(Self)
    }
}

impl Drop for PageBenchmarkModule {
    fn drop(&mut self) {
        pr_info!("Exiting single-page benchmark module.\n");
    }
}

/// Number of iterations for the test.
const NUM_ITERATIONS: usize = 5_000_000;
const ITERATION: i32 = 2;
#[no_mangle]
#[inline(never)]
/// Function to test page allocation, write, and read.
fn test_page_operations() {
    let mut allocate_time = 0i64;
    let mut write_time = 0i64;
    let mut read_time = 0i64;


    let mut buffer = [7u8; 4096]; // Buffer for write/read operations

    for _ in 0..NUM_ITERATIONS {
        // Allocate the page
        let start = Ktime::ktime_get();
        let page = allocate_page();
        let end = Ktime::ktime_get();
        allocate_time += ktime_ns_delta(end, start);

        if let Some(ref p) = page {
            // Write to the page
            let start = Ktime::ktime_get();
            write_page(p, &buffer);
            let end = Ktime::ktime_get();
            write_time += ktime_ns_delta(end, start);

            // Read from the page
            let start = Ktime::ktime_get();
            read_page(p, &mut buffer);
            let end = Ktime::ktime_get();
            read_time += ktime_ns_delta(end, start);
        }

        // Free the page
    }

    pr_info!("Total time to allocate: {} ms\n", Ktime::from_raw(allocate_time).to_ms());
    pr_info!("Total time to write: {} ms\n", Ktime::from_raw(write_time).to_ms());
    pr_info!("Total time to read: {} ms\n", Ktime::from_raw(read_time).to_ms());
}
#[no_mangle]
#[inline(never)]
/// Function to allocate a single page.
fn allocate_page() -> Option<Page> {
    match Page::alloc_page(GFP_KERNEL) {
        Ok(page) => Some(page),
        Err(_) => {
            pr_err!("Failed to allocate page.\n");
            None
        }
    }
}
#[no_mangle]
#[inline(never)]
/// Function to write to a single page.
fn write_page(page: &Page, buffer: &[u8]) {
    let len = buffer.len();
    unsafe {
        if let Err(e) = page.write_raw(buffer.as_ptr(), 0, len) {
            pr_err!("Rust Page Benchmark: Failed to write to page: {:?}\n", e);
        }
    }
}
#[no_mangle]
#[inline(never)]
/// Function to read from a single page.
fn read_page(page: &Page, buffer: &mut [u8]) {
    let len = buffer.len();
    unsafe {
        if let Err(e) = page.read_raw(buffer.as_mut_ptr(), 0, len) {
            pr_err!("Rust Page Benchmark: Failed to read from page: {:?}\n", e);
        }
    }
}

/// Returns the difference between two ktimes in MS
fn ktime_ns_delta(later: Ktime, earlier: Ktime)-> i64{
    (later-earlier).to_ns()
}