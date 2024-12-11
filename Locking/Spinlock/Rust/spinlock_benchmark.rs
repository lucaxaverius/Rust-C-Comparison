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
        for i in 0..3 {
            let work_item = SpinLockWork::new(spinlock.clone(), i)?;
            let _ = workqueue::system_unbound().enqueue(work_item);
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
        pr_info!(
            "Thread {} attempting to acquire spinlock\n",
            this.thread_id
        );
        let mut guard = this.spinlock.lock();
        pr_info!("Thread {} acquired spinlock\n", this.thread_id);
        // Simulate some operation
        guard.value += 1;
        pr_info!(
            "Thread {} incremented value to: {}\n",
            this.thread_id,
            guard.value
        );
        // Simulate delay
        simulate_delay(250);
        pr_info!("Thread {} releasing spinlock\n", this.thread_id);
        // Guard is dropped here
    }
}
