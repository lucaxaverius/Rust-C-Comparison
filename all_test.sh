#!/bin/bash

#Run List test
#cd ./LinkedList || exit
#./list_test.sh

#Run Mutex test
cd ./Locking/Mutex || exit
./mutex_test.sh

#Run Page test
cd ../../Memory || exit
./page_test.sh

#Run RBtree test
cd ../RBtree || exit
./rbtree_test.sh