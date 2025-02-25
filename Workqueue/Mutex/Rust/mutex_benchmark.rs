// SPDX-License-Identifier: GPL-2.0

//! Test module for RwLock, Mutex, and Spinlock.

use kernel::{
    prelude::*,
    sync::{
        new_mutex,
        Arc,
        Mutex,
    },
    workqueue::{self, impl_has_work, new_work, Work, WorkItem},
};

module! {
    type: MutexTestModule,
    name: "mutex_test_module",
    author: "Luca Saverio Esposito",
    description: "Test module for Mutex",
    license: "GPL",
}

const NUM_WORK_ITEMS: u32 = 3;
const NUM_ITERATIONS: u32 = 1000; 


struct SharedData {
    value: u32,
}

struct MutexTestModule {
    mutex: Arc<Pin<Box<Mutex<SharedData>>>>,
}

impl kernel::Module for MutexTestModule {
    fn init(_module: &'static ThisModule) -> Result<Self> {
        pr_info!("MutexTestModule init\n");

        // Initialize the shared data structures and wrap them in Arc
        let mutex = Arc::new(Box::pin_init(
            new_mutex!(SharedData { value: 2 }), GFP_KERNEL
        )?,GFP_KERNEL)?;

        let module = Self {
            mutex,
        };

        // Start test threads
        module.test_mutex()?;

        Ok(module)
    }
}

impl MutexTestModule {
    fn test_mutex(&self) -> Result {
        pr_info!("Testing Mutex\n");

        let mutex = self.mutex.clone();

        // Create mutex work items
        for i in 0..NUM_WORK_ITEMS {
            let work_item = MutexWork::new(mutex.clone(), i)?;
            let _ = workqueue::system_long().enqueue(work_item); 
        }

        Ok(())
    }
}

impl Drop for MutexTestModule {
    fn drop(&mut self) {
        pr_info!("MutexTestModule exit\n");
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
struct MutexWork {
    thread_id: usize,
    #[pin]
    work: Work<MutexWork>,
    mutex: Arc<Pin<Box<Mutex<SharedData>>>>,
    start: Ktime,
    end: Ktime,
}

impl_has_work! {
    impl HasWork<Self> for MutexWork { self.work }
}

impl MutexWork {
    fn new(
        mutex: Arc<Pin<Box<Mutex<SharedData>>>>,
        thread_id: usize,
    ) -> Result<Arc<Self>> {
        Arc::pin_init(
            pin_init!(MutexWork {
                thread_id,
                mutex,
                work <- new_work!("MutexWork::work"),
            }),
            GFP_KERNEL,
        )
    }
}

impl WorkItem for MutexWork {
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

            let mut guard = this.mutex.lock();
            
            pr_info!("Work item {} acquired mutex\n", this.thread_id);
            
            the_value = guard.value;
            pr_info!("Work item {} incremented value to: {}\n", this.thread_id, the_value,);

            pr_info!("Work item {} releasing mutex\n", this.thread_id);
            // Guard is dropped here
        }
        this.end = Ktime::ktime_get();
        pr_info!("Work item {} completed \n. Execution time: {} ms", this.thread_id, ktime_ms_delta(this.end,this.start));

    }
}
