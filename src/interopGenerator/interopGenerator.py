import os
import matplotlib.pyplot as plt
from interop import py_interop_plot, py_interop_run_metrics, py_interop_run

run_folder = "/run/user/1000/gvfs/smb-share:server=bigbird.ibb.gatech.edu,share=ngs/NovaSeq/EH08/"

def qscoreHistogram( inputString ):

	run_folder = inputString	
	
	run_metrics = py_interop_run_metrics.run_metrics()

	valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
	valid_to_load[py_interop_run.Q]=1

	run_metrics.read(run_folder, valid_to_load)

	bar_data = py_interop_plot.bar_plot_data()
	boundary = 30
	options = py_interop_plot.filter_options(run_metrics.run_info().flowcell().naming_method())
	
	py_interop_plot.plot_qscore_histogram(run_metrics, options, bar_data, boundary)
	
	for i in range(bar_data.size()):
	    x = [bar_data.at(i).at(j).x() for j in range(bar_data.at(i).size())]
	    y = [bar_data.at(i).at(j).y() for j in range(bar_data.at(i).size())]
	    w = [bar_data.at(i).at(j).width() for j in range(bar_data.at(i).size())]
	    plt.bar(x, y, width=w, color=bar_data.at(i).color())
	    

	plt.xlabel(bar_data.xyaxes().x().label(), fontsize=10)
	plt.ylabel(bar_data.xyaxes().y().label(), fontsize=10)
	plt.title(bar_data.title(), fontsize=10)
	plt.ylim([bar_data.xyaxes().y().min(), bar_data.xyaxes().y().max()])
	plt.xlim([bar_data.xyaxes().x().min(), bar_data.xyaxes().x().max()])
	plt.show()
	
	return plt

def qscoreHeatmap( inputString ):

	run_folder = inputString	
	
	run_metrics = py_interop_run_metrics.run_metrics()

	valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
	valid_to_load[py_interop_run.Q]=1

	run_metrics.read(run_folder, valid_to_load)

	heatmap_data = py_interop_plot.heatmap_data()
	boundary = 30
	options = py_interop_plot.filter_options(run_metrics.run_info().flowcell().naming_method())

	py_interop_plot.plot_qscore_heatmap(run_metrics, options, heatmap_data)
	
	'''
	for i in range(heatmap_data.size()):
	    x = [heatmap_data.at(i).at(j).x() for j in range(heatmap_data.at(i).size())]
	    y = [heatmap_data.at(i).at(j).y() for j in range(heatmap_data.at(i).size())]
	    w = [heatmap_data.at(i).at(j).width() for j in range(heatmap_data.at(i).size())]
	    plt.bar(x, y, width=w, color=heatmap_data.at(i).color())
	    
	'''
	plt.xlabel(heatmap_data.xyaxes().x().label(), fontsize=10)
	plt.ylabel(heatmap_data.xyaxes().y().label(), fontsize=10)
	plt.title(heatmap_data.title(), fontsize=10)
	plt.ylim([heatmap_data.xyaxes().y().min(), heatmap_data.xyaxes().y().max()])
	plt.xlim([heatmap_data.xyaxes().x().min(), heatmap_data.xyaxes().x().max()])
	plt.show()
	
	
	return plt

def errorExtraction( inputString ):

	run_folder = inputString
	
	run_metrics = py_interop_run_metrics.run_metrics()
	valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
	
	valid_to_load[py_interop_run.Error]=1
	
	run_metrics.read(run_folder, valid_to_load)
	
	error_metrics = run_metrics.error_metric_set()
	
	all_error_metrics = error_metrics.metrics()
	
	print(all_error_metrics[0].id())
	
	return

def main():
	
	errorExtraction(run_folder)
	
	'''
	qscoreHistogramActual = qscoreHistogram(run_folder)
	qscoreHistogramActual.show()
	'''
	'''
	qscoreHeatmapActual = qscoreHeatmap(run_folder)
	qscoreHeatmapActual.show()
	'''
	return

main()
