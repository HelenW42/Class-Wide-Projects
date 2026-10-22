#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <assert.h>

#ifndef STRIDE
#define STRIDE 1
#endif

// #define AXPY
// #define DOT
// #define ELEM

void shuffle(uint64_t* indices, uint64_t size)
{
	for (uint64_t i = size-1; i > 0; --i) {
        uint64_t swapind = rand() % i;
		double tmp = indices[i];
		indices[i] = indices[swapind];
		indices[swapind] = tmp;
    }
}

int main(int argc, char* argv[])
{
	uint64_t size = atoi(argv[1]);
	srand(time(NULL));
	double* x = (double*)malloc(size * sizeof(double));
	double* y  = malloc(size * sizeof(double));
	double* z = malloc(size * sizeof(double));
	for (uint64_t i = 0; i < size; i++)
	{
		y[i] = rand();
		x[i] = rand();
	}
#ifdef GATHER
	uint64_t* idx = malloc(size * sizeof(uint64_t));
	for (uint64_t i = 0; i < size; i++)
	{
		idx[i] = i;
	}
	shuffle(idx, size);
#endif
#ifdef AXPY
	double a = rand();
	uint64_t gflops = 2*sizeof(double)*size;
	for(int numruns = 0; numruns < 10; numruns++)
	{
		struct timespec ti, tf;
		struct timespec reqtime;
        reqtime.tv_sec = 0;
        reqtime.tv_nsec = 500000;
        nanosleep(&reqtime, NULL);
		for(int warmup = 0; warmup < 4; warmup++)
		{
			for (uint64_t i = 0; i<size; i+=STEP)
			{
#ifndef GATHER
				z[i] = a*x[i]+y[i];
#elifdef GATHER
				z[idx[i]] = a*x[idx[i]]+y[idx[i]];
#endif
			}
		}
		clock_gettime(CLOCK_MONOTONIC, &ti);
		for (uint64_t i = 0; i<size; i+=STEP)
		{
#ifndef GATHER
			z[i] = a*x[i]+y[i];
#elifdef GATHER
			z[idx[i]] = a*x[idx[i]]+y[idx[i]];
#endif
		}
		clock_gettime(CLOCK_MONOTONIC, &tf);
		double time_i = ti.tv_sec * 1e-9 + ti.tv_nsec;
		double time_f = tf.tv_sec * 1e-9 + tf.tv_nsec;
		double dur = time_f - time_i;
		printf("%ld,%ld,%lf\n", size, gflops, dur);
	}
#elifdef DOT
	uint64_t gflops = 2*sizeof(double)*size;
	for(int numruns = 0; numruns < 10; numruns++)
	{
		struct timespec ti, tf;
		struct timespec reqtime;
        reqtime.tv_sec = 0;
        reqtime.tv_nsec = 500000;
        nanosleep(&reqtime, NULL);
		for(int warmup = 0; warmup < 4; warmup++)
		{
			double sum = 0;
			for (uint64_t i = 0; i<size; i+=STEP)
			{
#ifndef GATHER
				sum += x[i]*y[i];
#elifdef GATHER
				sum += x[idx[i]]*y[idx[i]];
#endif
			}
		}
		double sum = 0;
		clock_gettime(CLOCK_MONOTONIC, &ti);
		for (uint64_t i = 0; i<size; i+=STEP)
		{
#ifndef GATHER
			sum += x[i]*y[i];
#elifdef GATHER
			sum += x[idx[i]]*y[idx[i]];
#endif
		}
		clock_gettime(CLOCK_MONOTONIC, &tf);
		double time_i = 10e-9 * ti.tv_sec + ti.tv_nsec;
		double time_f = 10e-9 * tf.tv_sec + tf.tv_nsec;
		printf("dot,%ld,%ld,%lf\n", size, gflops, time_f - time_i);
	}
#elifdef ELEM
	uint64_t gflops = sizeof(double)*size;
	for(int numruns = 0; numruns < 10; numruns++)
	{
		struct timespec ti, tf;
		struct timespec reqtime;
        reqtime.tv_sec = 0;
        reqtime.tv_nsec = 500000;
        nanosleep(&reqtime, NULL);
		for(int warmup = 0; warmup < 4; warmup++)
		{
			for (uint64_t i = 0; i<size; i+=STEP)
			{
#ifndef GATHER
				z[i] = x[i]*y[i];
#elifdef GATHER
				z[idx[i]] = x[idx[i]]*y[idx[i]];
#endif
			}
		}
		clock_gettime(CLOCK_MONOTONIC, &ti);
		for (uint64_t i = 0; i<size; i+=STEP)
		{
#ifndef GATHER
			z[i] = x[i]*y[i];
#elifdef GATHER
			z[idx[i]] = x[idx[i]]*y[idx[i]];
#endif
		}
		clock_gettime(CLOCK_MONOTONIC, &tf);
		double time_i = 10e-9 * ti.tv_sec + ti.tv_nsec;
		double time_f = 10e-9 * tf.tv_sec + tf.tv_nsec;
		printf("elem,%ld,%ld,%lf\n", size, gflops, time_f - time_i);
	}
#endif
	free(x);
	free(y);
	free(z);
#ifdef GATHER
	free(idx);
#endif
}
