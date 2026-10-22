#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <assert.h>

int main(int argc, char* argv[])
{
	uint64_t size = atoi(argv[1]);
	srand(time(NULL));
	double* x = (double*)malloc(size * sizeof(double));
	double* y  = malloc(size * sizeof(double));
	double* z = malloc(size * sizeof(double));
	for (int i = 0; i < size; i++)
	{
		y[i] = rand();
		x[i] = rand();
	}
#ifdef AXPY
	double a = rand();
	int gflops = 2*sizeof(double)*size;
	for(int numruns = 0; numruns < 10; numruns++)
	{
		struct timespec ti, tf;
		struct timespec reqtime;
        reqtime.tv_sec = 0;
        reqtime.tv_nsec = 500000;
        nanosleep(&reqtime, NULL);
		for(int warmup = 0; warmup < 4; warmup++)
		{
			for (uint64_t i = 0; i<size; i++)
			{
				z[i] = a*x[i]+y[i];
			}
		}
		clock_gettime(CLOCK_MONOTONIC, &ti);
		for (uint64_t i = 0; i<size; i++)
		{
			z[i] = a*x[i]+y[i];
		}
		clock_gettime(CLOCK_MONOTONIC, &tf);
		double time_i = ti.tv_sec * 1e-9 + ti.tv_nsec;
		double time_f = tf.tv_sec * 1e-9 + tf.tv_nsec;
		double dur = time_f - time_i;
		printf("%ld,%ld,%lf\n", size, gflops, dur);
	}
#elifdef DOT
	double sum = 0;
	int gflops = 2*sizeof(double)*size;
	for(int numruns = 0; numruns < 10; numruns++)
	{
		struct timespec ti, tf;
		struct timespec reqtime;
        reqtime.tv_sec = 0;
        reqtime.tv_nsec = 500000;
        nanosleep(&reqtime, NULL);
		for(int warmup = 0; warmup < 4; warmup++)
		{
			for (uint64_t i = 0; i<size; i++)
			{
				sum += x[i]*y[i];
			}
		}
		clock_gettime(CLOCK_MONOTONIC, &ti);
		for (uint64_t i = 0; i<size; i++)
		{
			sum += x[i]*y[i];
		}
		clock_gettime(CLOCK_MONOTONIC, &tf);
		double time_i = 10e-9 * ti.tv_sec + ti.tv_nsec;
		double time_f = 10e-9 * tf.tv_sec + tf.tv_nsec;
		printf("dot,%ld,%ld,%lf\n", size, gflops, time_f - time_i);
	}
#elifdef ELEM
	int gflops = sizeof(double)*size;
	for(int numruns = 0; numruns < 10; numruns++)
	{
		struct timespec ti, tf;
		struct timespec reqtime;
        reqtime.tv_sec = 0;
        reqtime.tv_nsec = 500000;
        nanosleep(&reqtime, NULL);
		for(int warmup = 0; warmup < 4; warmup++)
		{
			for (uint64_t i = 0; i<size; i++)
			{
				z[i] = x[i]*y[i];
			}
		}
		clock_gettime(CLOCK_MONOTONIC, &ti);
		for (uint64_t i = 0; i<size; i++)
		{
			z[i] = x[i]*y[i];
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
}
