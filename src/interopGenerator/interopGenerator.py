import os
import matplotlib.pyplot as plt
import matplotlib.figure as figure
import numpy
import pandas as pd
import seaborn as sns
from interop import py_interop_plot, py_interop_run_metrics, py_interop_run, py_interop_table, core
from mpl_toolkits import axes_grid1

#run_folder = "/run/user/1000/gvfs/smb-share:server=bigbird.ibb.gatech.edu,share=ngs/NovaSeq/EH08/"

run_folder = "/run/user/1000/gvfs/smb-share:server=heisenberg.local,share=ngs_raw/ARCHIVE/NextSeq/MW52/MW52-203005807/"

#run_folder = "/run/user/1000/gvfs/smb-share:server=heisenberg.local,share=ngs_raw/ARCHIVE/NextSeq/VM01/VM01-203587400/"

miColor="flare_r"


def add_colorbar(im, aspect=20, pad_fraction=0.5, **kwargs):
	"""Add a vertical color bar to an image plot."""
	
	divider = axes_grid1.make_axes_locatable(im.axes)
	width = axes_grid1.axes_size.AxesY(im.axes, aspect=1./aspect)
	pad = axes_grid1.axes_size.Fraction(pad_fraction, width)
	current_ax = plt.gca()
	cax = divider.append_axes("right", size=width, pad=pad)
	plt.sca(current_ax)
    
	return im.axes.figure.colorbar(im, cax=cax, **kwargs)

def axFormatter(ax):
	
	ax.spines['top'].set_visible(False)
	#ax.spines['bottom'].set_visible(False)
	ax.spines['right'].set_visible(False)
	#ax.spines['left'].set_visible(False)
	
	ax.set_facecolor("#F9E8DB")
	ax.grid(color="white")
	ax.set_axisbelow(True)
	
	return ax

def densityPerLane( inputString ):

	run_folder = inputString
	
	run_metrics = py_interop_run_metrics.run_metrics()
	valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
	
	valid_to_load[py_interop_run.Tile]=1
	
	run_metrics.read(run_folder, valid_to_load)
	#run_indexing = core.summary(run_folder, level="Lane")
	
	tile_metrics = run_metrics.tile_metric_set()
	
	tile_lane = []
	tile_density = []
	tile_density_passed = []
	
	for i in range(tile_metrics.size()):
		tile_lane.append(tile_metrics.at(i).lane())
		tile_density.append(tile_metrics.at(i).cluster_density_k())
		tile_density_passed.append(tile_metrics.at(i).cluster_density_pf_k())
	
	#print(vars(tile_metrics))
	#print(dir(tile_metrics))
	#print(run_indexing.dtype)
	
	#sampleLane = run_indexing["Lane"]
	#sampleDensity = run_indexing["Density"]
	
	#print(sampleLane)
	
	fig = plt.figure()
	ax1 = sns.boxplot(x=tile_lane, y=tile_density, showfliers=False, boxprops=dict(color="#7F2F70", edgecolor="black"))
		
	ax1 = sns.boxplot(x=tile_lane, y=tile_density_passed, showfliers=False, boxprops=dict(color="#D44D5F", edgecolor="black"))
	for line in ax1.get_lines():
		line.set_color("black")
		
	ax1 = axFormatter(ax1)
	fig = figFormatter(fig)
	
	plt.ylabel("Cluster Density (k/mm2)", fontsize=10)
	plt.xlabel("Lane", fontsize=10)
	plt.title("Data by Lane: Cluster Density", fontsize=15)
	
	plt.savefig("/home/mecore/Desktop/timp/testing_ground/cluster_density.jpg")
	
	plt.clf()
	
	return

def errorExtraction( inputString ):
	
	run_folder = inputString
	
	run_metrics = py_interop_run_metrics.run_metrics()
	valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
	
	valid_to_load[py_interop_run.Error]=1
	
	run_metrics.read(run_folder, valid_to_load)
	run_imaging = core.imaging(run_metrics)
	
	#error_rate_matrix = numpy.zeros((run_imaging.shape[0], 2))
	
	#for index, x in enumerate(run_imaging):
	#	error_rate_matrix[index, :] = [x["Cycle"], x["Error Rate"]]
		#print(error_rate_matrix[index,:])
	#numpy.savetxt("test.csv", run_imaging)
	
	plt.xlim([run_imaging["Cycle"].min(), run_imaging["Cycle"].max()])
	
	fig = plt.figure()
	ax = sns.boxplot(x=run_imaging["Cycle"], y=run_imaging["Error Rate"], showfliers=False, palette=miColor,order=range(int(run_imaging["Cycle"].min()), int(run_imaging["Cycle"].max())))
	
	ax = axFormatter(ax)
	fig = figFormatter(fig)
	
	for index, label in enumerate(ax.xaxis.get_ticklabels()):
		if (index + 1) % 10 != 0:
			label.set_visible(False)
	
	plt.ylabel("Error Rate", fontsize=10)
	plt.xlabel("Cycle", fontsize=10)
	plt.title("Data by Cycle: Error Rate", fontsize=15)
	
	plt.savefig("/home/mecore/Desktop/timp/testing_ground/error_rate.jpg")
	
	plt.clf()
	
	return

def figFormatter(fig):

	fig.set_size_inches(18.5,10.5)
	
	return fig

def percentOccupiedPerLane( inputString ):
	
	run_folder = inputString
	run_metrics = py_interop_run_metrics.run_metrics()
	
	valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
	valid_to_load[py_interop_run.ExtendedTile]=1
	
	run_metrics.read(run_folder, valid_to_load)
    	
	#print(dir(run_metrics))
	
	extended_tile_metrics = run_metrics.extended_tile_metric_set()
	'''
	for i in range(extended_tile_metrics.size()):
		print(extended_tile_metrics.at(i).percent_occupied())
	
	
	run_folder = inputString
	
	run_metrics = py_interop_run_metrics.run_metrics()
	valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
	a
	valid_to_load[py_interop_run.Error]=1
	
	run_metrics.read(run_folder, valid_to_load)
	run_indexing = core.indexing(run_folder)
	
	print(run_indexing.dtype)
	
	fig = plt.figure()	
	ax1 = sns.boxplot(x=tile_lane, y=tile_percent_occ, showfliers=False, boxprops=dict(color="#D44D5F", edgecolor="black"))
	for line in ax1.get_lines():
		line.set_color("black")
		
	ax1 = axFormatter(ax1)
	fig = figFormatter(fig)
	'''
	#plt.ylabel("Cluster Density (k/mm2)", fontsize=10)
	#plt.xlabel("Lane", fontsize=10)
	#plt.title("Data by Lane: Cluster Density", fontsize=15)
	
	#plt.show()
	#plt.clf()
	
	return

def qscoreHistogram( inputString ):

	#fig, ax = plt.subplots()
	
	run_folder = inputString	
	
	run_metrics = py_interop_run_metrics.run_metrics()

	valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
	valid_to_load[py_interop_run.Q]=1

	run_metrics.read(run_folder, valid_to_load)

	bar_data = py_interop_plot.bar_plot_data()
	#print(vars(bar_data))
	boundary = 5
	options = py_interop_plot.filter_options(run_metrics.run_info().flowcell().naming_method())
	
	fig, ax = plt.subplots()
	py_interop_plot.plot_qscore_histogram(run_metrics, options, bar_data, boundary)
	
	for i in range(bar_data.size()):
		x = [bar_data.at(i).at(j).x() for j in range(bar_data.at(i).size())]
		if x == [30,30]:
			continue
				
		y = [bar_data.at(i).at(j).y() for j in range(bar_data.at(i).size())]
		w = [bar_data.at(i).at(j).width() for j in range(bar_data.at(i).size())]
		
		print(i, bar_data.at(i).color(), x, y, w)
		
		if bar_data.at(i).color() == "Blue":
			myColor = "#481C48"
		elif bar_data.at(i).color() == "DarkGreen":
			myColor = "#EE533F"
		else:
			myColor = "#E30B5D"

		ax.bar(x, y, width=w, align="edge", color=myColor, edgecolor='w')
	    	#plt.text(x, y, str(y))

	ax = axFormatter(ax)
	fig = figFormatter(fig)
	
	plt.xlabel(bar_data.xyaxes().x().label(), fontsize=20)
	plt.ylabel(bar_data.xyaxes().y().label(), fontsize=20)
	plt.title(bar_data.title(), fontsize=25)
	plt.ylim([bar_data.xyaxes().y().min(), bar_data.xyaxes().y().max()])
	plt.xlim([bar_data.xyaxes().x().min(), bar_data.xyaxes().x().max()])
	
	
	plt.savefig("/home/mecore/Desktop/timp/testing_ground/qscore_histogram.jpg")
	
	plt.clf()
	
	return 

def qscoreHeatmap( inputString ):

	run_folder = inputString	
	
	run_metrics = py_interop_run_metrics.run_metrics()

	valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
	valid_to_load[py_interop_run.Q]=1

	run_metrics.read(run_folder, valid_to_load)

	heatmap_data = py_interop_plot.heatmap_data()
	
	
	hcol = heatmap_data.column_count()
	hrow = heatmap_data.row_count()
	heatmap_data.resize(hrow * 3, hcol)
	
	
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
	
	heatmap_matrix_holder = numpy.asmatrix(heatmap_ar)
	
	heatmap_matrix = numpy.asmatrix(numpy.zeros(shape=(heatmap_matrix_holder.shape[0] * 8, heatmap_matrix_holder.shape[1])))
	
	for i in range(heatmap_matrix_holder.shape[0]):
		for j in range(8):
			heatmap_matrix[i * 8 + j] = heatmap_matrix_holder[i,:]

	
	for i in range(heatmap_matrix.shape[1]):
		for j in reversed(range(heatmap_matrix.shape[0])):
			#print(j)
			if j >= 1:
				if heatmap_matrix[j-1, i] != heatmap_matrix[j, i]:
					heatmap_matrix[j-1, i] = (heatmap_matrix[j,i] - heatmap_matrix[j-1,i]) * 0.9 + heatmap_matrix[j-1, i]

	fig = plt.figure()
	yrange = numpy.arange(heatmap_data.xyaxes().y().min(), heatmap_data.xyaxes().y().max()+1, 0.125)
	
	ax = sns.heatmap(heatmap_matrix, yticklabels=yrange, cmap=miColor, cbar_kws={"label": '% of Max'})
	ax.tick_params(length=0)
	
	for index, label in enumerate(ax.yaxis.get_ticklabels()):
		if index % 32 != 0 and label != 40.0:
			label.set_visible(False)
	
	fig = figFormatter(fig)
	
	plt.xlabel(heatmap_data.xyaxes().x().label(), fontsize=10)
	plt.ylabel(heatmap_data.xyaxes().y().label(), fontsize=10)
	plt.title(heatmap_data.title() + ": Q-Score Heatmap", fontsize=15)
	plt.ylim([heatmap_data.xyaxes().y().min(), heatmap_data.xyaxes().y().max()*8])
	plt.xlim([heatmap_data.xyaxes().x().min(), heatmap_data.xyaxes().x().max()])
	plt.xticks(rotation=45)
	
	plt.savefig("/home/mecore/Desktop/timp/testing_ground/qscore_heatmap.jpg")
	plt.clf()
	
	return

def main():
	
	errorExtraction(run_folder)
	densityPerLane(run_folder)
	
	qscoreHistogramActual = qscoreHistogram(run_folder)
	qscoreHeatmapActual = qscoreHeatmap(run_folder)
	percentOccupiedPerLane(run_folder)

	
	return

main()
