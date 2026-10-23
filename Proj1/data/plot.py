import matplotlib.pyplot as plt
import numpy as np
import csv
from matplotlib.ticker import LogLocator

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
		numvalid = 0
		for j in range(i, i+10):
			input_time = float(list[j])
			
			if input_time < min_time:
				min_time = input_time
			if input_time > max_time:
				max_time = input_time

			if input_time > 0:
				curr_time += input_time
				numvalid+=1
		
		time.append(curr_time/numvalid)
		time_err.append(max_time-min_time)
		curr_time = 0.0
		min_time=np.inf
		max_time=-np.inf
	return time, time_err

def read_gflop(time, time_err, flop):
	gflops = []
	gflops_err = []
	for i in range(0,len(time)):
		if time[i] > 0: gflops.append((flop[i])/(time[i]))
		else: gflops.append(0)
		if ((time[i] + time_err[i]/2)*1e-9 > 0) and ((time[i] - time_err[i]/2)*1e-9 > 0): 
			gflops_err.append((flop[i]*1e-9)/((time[i] - time_err[i])/2*1e-9)-(flop[i]*1e-9)/((time[i] + time_err[i])/2*1e-9))
		else: gflops_err.append(0)
	return gflops, gflops_err

def read_data(file):
	data = []
	with open(file, newline='\n') as csvfile:
		file_reader = csv.reader(csvfile)
		for row in file_reader:
			data.append(row)
	return data

def plot_gflop_size(ax, title, output_file, sizes, gflops_scalar, gflops_simd):
	# plot:
	ax.plot(sizes, gflops_scalar, label="scalar", color="tab:blue")
	ax.plot(sizes, gflops_simd, label="simd", color="tab:orange")

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
	y_lo = min(min(gflops_scalar), min(gflops_simd))
	y_hi = max(max(gflops_scalar), max(gflops_simd))

	pad = 0.05 * (y_hi - y_lo) if y_hi > y_lo else max(abs(y_hi) * 0.05, 1.0)
	ax.set_ylim(y_lo - pad, y_hi + pad)

	ax.text(2, y_hi*0.8, "L1", horizontalalignment='left',
			verticalalignment='center',
			rotation='vertical')
	
	ax.text(48000, y_hi*0.8, "L2", horizontalalignment='left',
			verticalalignment='center',
			rotation='vertical')
	plt.axvline(x=48000, color='gainsboro')
	ax.text(2048000, y_hi*0.8, "L3", horizontalalignment='left',
			verticalalignment='center',
			rotation='vertical')
	plt.axvline(x=2048000, color='gainsboro')
	ax.text(2.4e7, y_hi*0.8, "DRAM", horizontalalignment='left',
			verticalalignment='center',
			rotation='vertical')
	plt.axvline(x=2.4e7, color='gainsboro')

	# ---- labels ----
	ax.set_xlabel("Size (Bytes)")
	ax.set_ylabel("GFLOP/s")
	ax.set_title(title)
	ax.grid(True, which="major", linestyle=":", alpha=0.6)

	plt.legend()
	plt.tight_layout()
	plt.savefig(output_file)

scalar_axpy_data = read_data('scalar_axpy.csv')
simd_axpy_data = read_data('simd_axpy.csv')

scalar_dot_data = read_data('scalar_dot.csv')
simd_dot_data = read_data('simd_dot.csv')

scalar_elem_data = read_data('scalar_elem.csv')
simd_elem_data = read_data('simd_elem.csv')

plt.style.use('_mpl-gallery')

sizes, flop_axpy = read_sizes_flops(scalar_axpy_data)
sizes, flop_dot = read_sizes_flops(scalar_dot_data)
sizes, flop_elem = read_sizes_flops(scalar_dot_data)

time_scalar_axpy, time_err_scalar_axpy = read_time([row[2] for row in scalar_axpy_data])
gflops_scalar_axpy, gflops_err_scalar_axpy = read_gflop(time_scalar_axpy, time_err_scalar_axpy, flop_axpy)

time_simd_axpy, time_err_simd_axpy = read_time([row[2] for row in simd_axpy_data])
gflops_simd_axpy, gflops_err_simd_axpy = read_gflop(time_simd_axpy, time_err_simd_axpy, flop_axpy)

time_scalar_dot, time_err_scalar_dot = read_time([row[2] for row in scalar_dot_data])
gflops_scalar_dot, gflops_err_scalar_dot = read_gflop(time_scalar_dot, time_err_scalar_dot, flop_dot)

time_simd_dot, time_err_simd_dot = read_time([row[2] for row in simd_dot_data])
gflops_simd_dot, gflops_err_simd_dot = read_gflop(time_simd_dot, time_err_simd_dot, flop_dot)


time_scalar_elem, time_err_scalar_elem = read_time([row[2] for row in scalar_elem_data])
gflops_scalar_elem, gflops_err_scalar_elem = read_gflop(time_scalar_elem, time_err_scalar_elem, flop_elem)

time_simd_elem, time_err_simd_elem = read_time([row[2] for row in simd_elem_data])
gflops_simd_elem, gflops_err_simd_elem = read_gflop(time_simd_elem, time_err_simd_elem, flop_elem)

fig, ax1 = plt.subplots(figsize=(8, 5.5))
plot_gflop_size(ax1, "axpy", "axpy_gflops.png", sizes, gflops_scalar_axpy, gflops_simd_axpy)

fig, ax2 = plt.subplots(figsize=(8, 5.5))
plot_gflop_size(ax2, "dot", "dot_gflops.png", sizes, gflops_scalar_dot, gflops_simd_dot)

fig, ax3 = plt.subplots(figsize=(8, 5.5))
plot_gflop_size(ax3, "elem", "elem_gflops.png", sizes, gflops_scalar_elem, gflops_simd_elem)
