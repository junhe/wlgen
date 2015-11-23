#include <iostream>
// #include <mpi.h>
#include <string>
#include <stdlib.h>
#include <assert.h>
#include <stdio.h>
#include <sys/time.h>
#include <time.h>

#include "SimplePattern.h"

using namespace std;

int main(int argc, char **argv)
{
    struct timeval start, end, result;

    // SimplePattern simplepattern(64, 32, 10, SEQUENTIAL, "/tmp/littletest");
    SimplePattern simplepattern(64, 32, 10, RANDOM, "/tmp/littletest");

    gettimeofday(&start, NULL);

    // run the workload
    simplepattern.run();

    gettimeofday(&end, NULL);

    timersub(&end, &start, &result);
    printf("result %ld.%ld\n", result.tv_sec, result.tv_usec);
    printf("start %ld.%ld\n", start.tv_sec, start.tv_usec);
    printf("end %ld.%ld\n", end.tv_sec, end.tv_usec);

    return 0;
}



