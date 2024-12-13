// SPDX-License-Identifier: GPL-2.0

//! Test module for Mutex.

use kernel::prelude::*;
use kernel::sync::{new_mutex,Mutex};
use kernel::time::*;

module! {
    type: MutexTestModule,
    name: "Rust_Mutex_Benchmark",
    author: "Luca Saverio Esposito",
    description: "Mutex Lock/Unlock Performance Test",
    license: "GPL",
}

#[pin_data]
struct Example {
    #[pin]
    m: Mutex<()>,
}

impl Example {
    fn new() -> impl PinInit<Self> {
        pin_init!(Self {
            m <- new_mutex!(()),
        })
    }
}

struct MutexTestModule;

impl kernel::Module for MutexTestModule {
    fn init(_module: &'static ThisModule) -> Result<Self> {
        pr_info!("Initializing Mutex Lock/Unlock Performance Test...\n");

        
        let mutex = KBox::pin_init(Example::new(), GFP_KERNEL).expect("Failed during mutex initialization");

        let num_iterations = 1_000_000;
        let mut total_lock_time = 0i64;
        let mut min_time = i64::MAX;
        let mut max_time = i64::MIN;

        let start = Ktime::ktime_get();
        for _ in 0..num_iterations {
            let lock_start = Ktime::ktime_get();

            {
                let _guard = mutex.m.lock(); // Lock and unlock the mutex
            }

            let lock_end = Ktime::ktime_get();
            let elapsed = ktime_ns_delta(lock_end,lock_start);
            
            total_lock_time += elapsed;
            if elapsed < min_time {
                min_time = elapsed;
            }
            if elapsed > max_time {
                max_time = elapsed;
            }
        }
        let end = Ktime::ktime_get();
        let total_time_ms =ktime_ms_delta(end,start);
        pr_info!("Mutex Test Completed\n");
        pr_info!("Total time: {} ms\n", total_time_ms);
        pr_info!("Total lock/unlock time: {} ms\n", Ktime::from_raw(total_lock_time).to_ms());
        pr_info!(
            "Average time per lock/unlock: {} ns\n",
            total_lock_time / num_iterations as i64
        );
        pr_info!("Minimum time per lock/unlock: {} ns\n", min_time);
        pr_info!("Maximum time per lock/unlock: {} ns\n", max_time);

        Ok(Self)
    }
}

impl Drop for MutexTestModule {
    fn drop(&mut self) {
        pr_info!("Exiting Mutex Lock/Unlock Performance Test.\n");
    }
}

/// Returns the difference between two ktimes in MS
fn ktime_ns_delta(later: Ktime, earlier: Ktime)-> i64{
    (later-earlier).to_ns()
}

