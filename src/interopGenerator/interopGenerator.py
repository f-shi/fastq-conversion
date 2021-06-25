import os
import matplotlib.pyplot as plt
import matplotlib.figure as figure
import numpy
from interop import py_interop_plot, py_interop_run_metrics, py_interop_run, imaging
from mpl_toolkits import axes_grid1

run_folder = "/run/user/1000/gvfs/smb-share:server=bigbird.ibb.gatech.edu,share=ngs/NovaSeq/EH08/"

def add_colorbar(im, aspect=20, pad_fraction=0.5, **kwargs):
	"""Add a vertical color bar to an image plot."""
	    
	divider = axes_grid1.make_axes_locatable(im.axes)
	width = axes_grid1.axes_size.AxesY(im.axes, aspect=1./aspect)
	pad = axes_grid1.axes_size.Fraction(pad_fraction, width)
	current_ax = plt.gca()
	cax = divider.append_axes("right", size=width, pad=pad)
	plt.sca(current_ax)
    
	return im.axes.figure.colorbar(im, cax=cax, **kwargs)

def qscoreHistogram( inputString ):

	run_folder = inputString	
	
	run_metrics = py_interop_run_metrics.run_metrics()

	valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
	valid_to_load[py_interop_run.Q]=1

	run_metrics.read(run_folder, valid_to_load)

	bar_data = py_interop_plot.bar_plot_data()
	#print(vars(bar_data))
	boundary = 30
	options = py_interop_plot.filter_options(run_metrics.run_info().flowcell().naming_method())
	
	py_interop_plot.plot_qscore_histogram(run_metrics, options, bar_data, boundary)
	
	for i in range(bar_data.size()):
		x = [bar_data.at(i).at(j).x() for j in range(bar_data.at(i).size())]
		if x == [30,30]:
			continue
				
		y = [bar_data.at(i).at(j).y() for j in range(bar_data.at(i).size())]
		w = [bar_data.at(i).at(j).width() for j in range(bar_data.at(i).size())]
		print(x, y, w)
		plt.bar(x, y, width=w, align="edge", color=bar_data.at(i).color())
	    	#plt.text(x, y, str(y))


	plt.xlabel(bar_data.xyaxes().x().label(), fontsize=10)
	plt.ylabel(bar_data.xyaxes().y().label(), fontsize=10)
	plt.title(bar_data.title(), fontsize=10)
	plt.ylim([bar_data.xyaxes().y().min(), bar_data.xyaxes().y().max()])
	plt.xlim([bar_data.xyaxes().x().min(), bar_data.xyaxes().x().max()])
	
	plt.savefig(os.path.join(run_folder, "Interop_Images", "QScore_Histogram.png"))
	
	#plt.show()
	
	return plt

def qscoreHeatmap( inputString ):

	run_folder = inputString	
	
	run_metrics = py_interop_run_metrics.run_metrics()

	valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
	valid_to_load[py_interop_run.Q]=1

	run_metrics.read(run_folder, valid_to_load)

	heatmap_data = py_interop_plot.heatmap_data()
	hcol = heatmap_data.column_count()
	hrow = heatmap_data.row_count()
	heatmap_data.resize(hrow * 2, hcol * 2)
	boundary = 30
	options = py_interop_plot.filter_options(run_metrics.run_info().flowcell().naming_method())

	py_interop_plot.plot_qscore_heatmap(run_metrics, options, heatmap_data)
	
	#print(type(heatmap_data.row_count()))
	heatmap_ar = numpy.empty((heatmap_data.column_count(), heatmap_data.row_count()))
	heatmap_floats = []
	rows = []
	cols = []

	
	for i in range(heatmap_data.row_count()):
		for j in range(heatmap_data.column_count()):
			heatmap_floats.append(heatmap_data.at(i,j))
			cols.append(i)
			rows.append(j)
			#print(type(heatmap_data.at(i,j)))
	
	heatmap_ar[rows,cols] = heatmap_floats
	#print(pos)
	#print(heatmap_floats)
	
	#for i in range(len(rows)):
	#	print(rows[i], cols[i], heatmap_floats[i])
	
	#plt.bar(x, y, width=w, color=heatmap_data.at(i).color())
	    
	
	hm_graph = plt.imshow(heatmap_ar, cmap='RdYlGn')
	
	plt.xlabel(heatmap_data.xyaxes().x().label(), fontsize=10)
	plt.ylabel(heatmap_data.xyaxes().y().label(), fontsize=10)
	plt.title(heatmap_data.title(), fontsize=10)
	plt.ylim([heatmap_data.xyaxes().y().min(), heatmap_data.xyaxes().y().max()])
	plt.xlim([heatmap_data.xyaxes().x().min(), heatmap_data.xyaxes().x().max()])
	plt.grid(which="minor", color="w", linestyle="-", linewidth=3)
	
	#cbar = plt.colorbar(hm_graph,fraction=0.046, pad = 0.04)
	cbar = add_colorbar(hm_graph)
	cbar.ax.set_ylabel("% of max", rotation=-90, va="bottom")
	
	plt.savefig(os.path.join(run_folder, "Interop_Images", "QScore_Heatmap.png"))
	
	plt.clf()
	
	return plt

def errorExtraction( inputString ):

	run_folder = inputString
	
	run_metrics = py_interop_run_metrics.run_metrics()
	valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
	
	valid_to_load[py_interop_run.Error]=1
	
	run_metrics.read(run_folder, valid_to_load)
	run_imaging = imaging(run_metrics)
	print(run_imaging.dtype)
	#numpy.savetxt("test.csv", run_imaging)
	
	print(numpy.asmatrix(run_imaging))
	
	summary_metrics = run_metrics.summary_run_metric_set()
	#error_metrics = run_metrics.error_metric_set()
	
	#print(dir(error_metrics))
	
	#all_error_metrics = error_metrics.metrics()
	#print("\n\n")
	#print(dir(all_error_metrics))
	
	return

def main():
	'''
	errorExtraction(run_folder)
	'''
	
	qscoreHistogramActual = qscoreHistogram(run_folder)
	#qscoreHeatmapActual = qscoreHeatmap(run_folder)
	
	return

main()
