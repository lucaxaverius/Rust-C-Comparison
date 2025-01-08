// SPDX-License-Identifier: GPL-2.0

//! Test module for Mutex.

use kernel::prelude::*;
use kernel::sync::{new_mutex,Mutex};
use kernel::time::*;
use kernel::alloc::allocator::Kmalloc;

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

/// Locks the mutex and returns the guard.
#[no_mangle]
#[inline(never)]
pub(crate) fn take_and_release(mutex: &Pin<Box<Example, Kmalloc>>){
    let guard = mutex.m.lock(); // Lock and unlock the mutex
    drop(guard);
}



struct MutexTestModule;

const NUM_ITERATIONS: usize = 20_000_000;
//const NUM_EXECUTION: usize = 30;
const ITERATION: i32 = 1;

impl kernel::Module for MutexTestModule {
    #[no_mangle]
    fn init(_module: &'static ThisModule) -> Result<Self> {
        pr_info!("Initializing Mutex Lock/Unlock Performance Test...\n");
        let mutex = KBox::pin_init(Example::new(), GFP_KERNEL).expect("Failed during mutex initialization\n");

        MutexTestModule::rust_mutex_test(&mutex,ITERATION);
        pr_info!("Iteration {} ended.\n", ITERATION);
        pr_info!("Test module completed.\n");
        Ok(Self)
    }
}

impl Drop for MutexTestModule {
    fn drop(&mut self) {
        pr_info!("Exiting Mutex Lock/Unlock Performance Test.\n");
    }
}

impl MutexTestModule{
    #[no_mangle]
    fn rust_mutex_test(mutex: &Pin<Box<Example, Kmalloc>>, count: i32){

        let mut total_lock_time = 0i64;
        let mut min_time = i64::MAX;
        let mut max_time = i64::MIN;

        let start = Ktime::ktime_get();
        for _ in 0..NUM_ITERATIONS
     {
           let lock_start = Ktime::ktime_get();
 
            take_and_release(&mutex);

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
        pr_info!("Mutex Test {} Completed\n", count);
        pr_info!("Total time: {} ms\n", total_time_ms);
        pr_info!("Total lock/unlock time: {} ms\n", Ktime::from_raw(total_lock_time).to_ms());
        pr_info!(
            "Average time per lock/unlock: {} ns\n",
            total_lock_time / NUM_ITERATIONS as i64
        ); 
        pr_info!("Minimum time per lock/unlock: {} ns\n", min_time);
        pr_info!("Maximum time per lock/unlock: {} ns\n", max_time);

    } 
}


/// Returns the difference between two ktimes in MS
fn ktime_ns_delta(later: Ktime, earlier: Ktime)-> i64{
    (later-earlier).to_ns()
}

