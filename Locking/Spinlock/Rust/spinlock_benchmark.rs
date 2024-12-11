// SPDX-License-Identifier: GPL-2.0

//! Test module for RwLock, Mutex, and Spinlock.

use kernel::{
    prelude::*,
    sync::{
        new_spinlock,
        Arc,
        SpinLock,
    },
    workqueue::{self, impl_has_work, new_work, Work, WorkItem},
};

module! {
    type: SpinLockTestModule,
    name: "spinlock_test_module",
    author: "Luca Saverio Esposito",
    description: "Test module for RwLock, Mutex, and Spinlock",
    license: "GPL",
}

const NUM_WORK_ITEMS: u32 = 3;
const NUM_ITERATIONS: u32 = 1000;

struct SharedData {
    value: u32,
}

struct SpinLockTestModule {
    spinlock: Arc<Pin<Box<SpinLock<SharedData>>>>,
}

impl kernel::Module for LockTestModule {
    fn init(_module: &'static ThisModule) -> Result<Self> {
        pr_info!("LockTestModule init\n");

        // Initialize the shared data structures and wrap them in Arc
        let spinlock = Arc::new(Box::pin_init(
            new_spinlock!(SharedData { value: 3 }), GFP_KERNEL
        )?,GFP_KERNEL)?;

        let module = Self {
            spinlock,
        };

        // Start test threads
        module.test_spinlock()?;

        Ok(module)
    }
}

impl LockTestModule {
   
    fn test_spinlock(&self) -> Result {
        pr_info!("Testing Spinlock\n");

        let spinlock = self.spinlock.clone();

        // Create spinlock work items
        for i in 0..NUM_WORK_ITEMS {
            let work_item = SpinLockWork::new(spinlock.clone(), i)?;
            let _ = workqueue::system_long().enqueue(work_item);
        }

        Ok(())
    }
}

impl Drop for LockTestModule {
    fn drop(&mut self) {
        pr_info!("LockTestModule exit\n");
    }
}

/// This function does dummy operation to simulate a delay
pub fn simulate_delay(delay: u32) {
    let mut a = 1;
    for _ in 0..delay {
        a = a + 1;
    }
}

#[pin_data]
struct SpinLockWork {
    thread_id: usize,
    #[pin]
    work: Work<SpinLockWork>,
    spinlock: Arc<Pin<Box<SpinLock<SharedData>>>>,
    start: Ktime,
    end: Ktime,
}

impl_has_work! {
    impl HasWork<Self> for SpinLockWork { self.work }
}

impl SpinLockWork {
    fn new(
        spinlock: Arc<Pin<Box<SpinLock<SharedData>>>>,
        thread_id: usize,
    ) -> Result<Arc<Self>> {
        Arc::pin_init(
            pin_init!(SpinLockWork {
                thread_id,
                spinlock,
                work <- new_work!("SpinLockWork::work"),
            }),
            GFP_KERNEL,
        )
    }
}

impl WorkItem for SpinLockWork {
    type Pointer = Arc<Self>;

    fn run(this: Arc<Self>) {
        this.start = Ktime::ktime_get();

        // Simulate some operation
        if this.thread_id == 0 {
            guard.value += 1;
        } else if this.thread_id == 1 {
            guard.value += 2;
        } else {
            guard.value += 3;
        
        }

        for _ in  0..NUM_ITERATIONS{

            let mut guard = this.spinlock.lock();
            
            pr_info!("Work item {} acquired spinlock\n", this.thread_id);
            
            the_value = guard.value;
            pr_info!("Work item {} incremented value to: {}\n", this.thread_id, the_value,);

            pr_info!("Work item {} releasing spinlock\n", this.thread_id);
            // Guard is dropped here
        }
        this.end = Ktime::ktime_get();
        pr_info!("Work item {} completed \n. Execution time: {} ms", this.thread_id, ktime_ms_delta(this.end,this.start));

    }
}
