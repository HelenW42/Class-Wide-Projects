#include "stdint.h"
#include "stdio.h"
#include "stdlib.h"
#include "time.h"

int main(int argc, char* argv[])
{
	uint64_t size = atoi(argv[1]);
	srand(time(NULL));
	double* x = (double*)malloc(size * sizeof(double));
	double* y  = malloc(size * sizeof(double));
	double* z = malloc(size * sizeof(double));

#ifdef AXPY
	double a = rand();
	for(int numruns = 0; numruns < 10; numruns++)
	{
		for(int warmup = 0; warmup < 4; warmup++)
		{
			for (uint64_t i = 0; i<size; i++)
			{
				z[i] = a*x[i]+y[i];
			}
		}
		for (uint64_t i = 0; i<size; i++)
		{
			z[i] = a*x[i]+y[i];
		}
	}
#elifdef DOT
	double sum = 0;
	for(int numruns = 0; numruns < 10; numruns++)
	{
		for(int warmup = 0; warmup < 4; warmup++)
		{
			for (uint64_t i = 0; i<size; i++)
			{
				sum += x[i]*y[i];
			}
		}
		for (uint64_t i = 0; i<size; i++)
		{
			sum += x[i]*y[i];
		}
	}
#elifdef ELEM
	for(int numruns = 0; numruns < 10; numruns++)
	{
		for(int warmup = 0; warmup < 4; warmup++)
		{
			for (uint64_t i = 0; i<size; i++)
			{
				z[i] = x[i]*y[i];
			}
		}
		for (uint64_t i = 0; i<size; i++)
		{
			z[i] = x[i]*y[i];
		}
	}
#endif
	free(x);
	free(y);
	free(z);
}
