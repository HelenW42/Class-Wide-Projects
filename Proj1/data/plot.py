import matplotlib.pyplot as plt
import numpy as np
import csv
from matplotlib.ticker import ScalarFormatter, FuncFormatter, LogFormatterSciNotation, NullFormatter, LogLocator

def fmt_power_of_two(value, _pos):
    """Label ticks as plain integers when >= 1, otherwise as fractions of 2^-k."""
    if value >= 1:
        return f"{value:,.0f}"
    return f"2$^{{{int(round(np.log2(value)))}}}$"

def fmt_power_of_ten(value, _pos):
    """Label ticks as plain integers when >= 1, otherwise as fractions of 10^-k."""
    if value >= 1:
        return f"{value:,.0f}"
    return f"10$^{{{int(round(np.log2(value)))}}}$"

def read_sizes_flops(list):
	flop = []
	sizes = []
	for i in range(0,len(list), 10):
		sizes.append(int(list[i][0]))
		flop.append(float(list[i][0]))
	return sizes, flop

def read_time(list):
	min_time=np.inf
	max_time=-np.inf
	curr_time = 0.0
	time = []
	time_err = []
	for i in range(0,len(list), 10):
		for j in range(i, i+10):
			input_time = float(list[j])
			
			if input_time < min_time:
				min_time = input_time
			if input_time > max_time:
				max_time = input_time
			
			curr_time += input_time
		
		time.append(curr_time/10.0)
		time_err.append(max_time-min_time)
		curr_time = 0.0
		min_time=np.inf
		max_time=-np.inf
	return time, time_err

def read_gflop(time, time_err, flop):
	gflops = []
	gflops_err = []
	for i in range(0,len(time)):
		if time[i] > 0: gflops.append((flop[i]*1e-9)/(time[i]*1e-9))
		else: gflops.append(0)
		if ((time[i] + time_err[i])*1e-9 > 0) and ((time[i] - time_err[i])*1e-9 > 0): gflops_err.append((flop[i]*1e-9)/((time[i] - time_err[i])**1e-9)-(flop[i]*1e-9)/((time[i] + time_err[i])**1e-9))
		else: gflops_err.append(0)
	return gflops, gflops_err



scalar_axpy_data = []
simd_axpy_data = []
simd_widest_axpy_data = []

with open('scalar_axpy.csv', newline='\n') as scalar_axpy:
	axpy_reader = csv.reader(scalar_axpy)
	for row in axpy_reader:
		scalar_axpy_data.append(row)


with open('simd_axpy.csv', newline='\n') as simd_axpy:
	axpy_reader = csv.reader(simd_axpy)
	for row in axpy_reader:
		simd_axpy_data.append(row)

with open('simd_widest_axpy.csv', newline='\n') as simd_axpy:
	axpy_reader = csv.reader(simd_axpy)
	for row in axpy_reader:
		simd_widest_axpy_data.append(row)

# with open('simd_axpy.csv', newline='\n') as simd_widest_axpy:
# 	axpy_reader = csv.reader(simd_widest_axpy)
# 	for row in axpy_reader:
# 		simd_widest_axpy_data.append(row)

plt.style.use('_mpl-gallery')

# get data:
sizes, flop = read_sizes_flops(scalar_axpy_data)

time_scalar, time_err_scalar = read_time([row[2] for row in scalar_axpy_data])
gflops_scalar, gflops_err_scalar = read_gflop(time_scalar, time_err_scalar, flop)

time_widest_simd, time_err_widest_simd = read_time([row[2] for row in simd_widest_axpy_data])
gflops_widest_simd, gflops_err_widest_simd = read_gflop(time_widest_simd, time_err_widest_simd, flop)

time_simd, time_err_simd = read_time([row[2] for row in simd_axpy_data])
gflops_simd, gflops_err_simd = read_gflop(time_simd, time_err_simd, flop)


# plot:
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.plot(sizes, gflops_scalar, label="scalar",#yerr=gflops_scalar_err,
			#fmt="o", markersize=5, capsize=3, elinewidth=1,
			color="tab:blue")#, ecolor="gray")
# ax.plot(sizes, gflops_simd, #yerr=gflops_scalar_err,
# 			#fmt="o", markersize=5, capsize=3, elinewidth=1,
# 			color="tab:cyan")#, ecolor="gray")
ax.plot(sizes, gflops_widest_simd, label="simd",#yerr=gflops_scalar_err,
			#fmt="o", markersize=5, capsize=3, elinewidth=1,
			color="tab:orange")#, ecolor="gray")

# ---- sizes axis: log base 2, range and ticks fitted to the data ----
ax.set_xscale("log", base=2)
x_lo = min(sizes)
x_hi = max(sizes)
k_min = int(np.floor(np.log2(x_lo)))
k_max = int(np.ceil(np.log2(x_hi)))
if k_min == k_max:
	k_max += 1
ax.set_xlim(2.0 ** k_min * 0.9, 2.0 ** k_max * 1.1)

# One tick per power of two; thin them out if the range is very wide.
step = max(1, int(np.ceil((k_max - k_min + 1) / 12)))
ax.set_xticks([2.0 ** k for k in range(k_min, k_max + 1, step)])
ax.xaxis.set_major_locator(LogLocator(base=2, numticks=15))

# ---- time axis: fit to data including error bars, with 5% padding ----
# ax.set_yscale("log", base=10)
y_lo = min([min(gflops_scalar), min(gflops_widest_simd), min(gflops_simd)])
y_hi = max([max(gflops_scalar), max(gflops_widest_simd), max(gflops_simd)])
print(y_lo)
print(y_hi)
pad = 0.05 * (y_hi - y_lo) if y_hi > y_lo else max(abs(y_hi) * 0.05, 1.0)
ax.set_ylim(y_lo - pad, y_hi + pad)
# ax.yaxis.set_major_formatter(LogFormatterSciNotation(base=10))
# ax.yaxis.set_minor_formatter(NullFormatter())  # minor ticks, no labels


# ---- labels ----
ax.set_xlabel("Size (Bytes)")
ax.set_ylabel("GFLOP/s")
ax.set_title("axpy")
ax.grid(True, which="major", linestyle=":", alpha=0.6)

ax.text(48000, 3.5, "L2")
ax.text(2048000, 3.5, "L3")
ax.text(2.4e7, 3.5, "DRAM")

plt.legend()
plt.tight_layout()
plt.show()
