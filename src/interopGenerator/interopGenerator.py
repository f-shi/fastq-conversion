import os
import matplotlib.pyplot as plt
import matplotlib.figure as figure
import numpy
import pandas as pd
import seaborn as sns
from interop import py_interop_plot, py_interop_run_metrics, py_interop_run, py_interop_table, core
from mpl_toolkits import axes_grid1

#run_folder = "/run/user/1000/gvfs/smb-share:server=bigbird.ibb.gatech.edu,share=ngs/NextSeq/MW56R/MW56R-207921767/"

run_folder = "/run/user/1000/gvfs/smb-share:server=bigbird.ibb.gatech.edu,share=ngs/NovaSeq/EH08/"

#run_folder = "/run/user/1000/gvfs/smb-share:server=heisenberg.local,share=ngs_raw/ARCHIVE/NextSeq/GG52/GG52-208826650/"

#run_folder = "/run/user/1000/gvfs/smb-share:server=heisenberg.local,share=ngs_raw/ARCHIVE/NextSeq/VM01/VM01-203587400/"

miColor="magma"


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
	#ax.set_facecolor("#f7F0eb")
	ax.grid(color="white")
	ax.set_axisbelow(True)
	
	return ax

def basePercent( inputString ):

	run_folder = inputString
	
	run_metrics = py_interop_run_metrics.run_metrics()
	valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
	
	valid_to_load[py_interop_run.CorrectedInt]=1
	
	run_metrics.read(run_folder, valid_to_load)
	run_imaging = core.imaging(run_metrics)
	
	run_cycle = run_imaging["Cycle"]
	run_a = run_imaging["% Base/A"]
	run_c = run_imaging["% Base/C"]
	run_g = run_imaging["% Base/G"]
	run_t = run_imaging["% Base/T"]
	
	fig,ax = plt.subplots()
	ax = sns.lineplot(x = run_cycle, y= run_a, color="#FF4500", label="A")
	ax = sns.lineplot(x = run_cycle, y= run_c, color="#4C1F4D", label="C")
	ax = sns.lineplot(x = run_cycle, y= run_g, color="orange", label="G")
	ax = sns.lineplot(x = run_cycle, y= run_t, color="black", label="T")
	
	plt.xlim(0, max(run_cycle))
	
	ax = axFormatter(ax)
	fig = figFormatter(fig)
	
	
	plt.ylabel("%Base", fontsize=20)
	plt.xlabel("Cycle", fontsize=20)
	plt.title("Data by Cycle: %Base", fontsize=25)
	
	plt.savefig(os.path.join(inputString, "Interop_Images", "4_percent_base_by_cycle.jpg"), dpi = 200, bbox_inches = 'tight', pad_inches=0.25, frameon=True)
	plt.clf()
	
	return

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
	ax1 = sns.boxplot(x=tile_lane, y=tile_density, showfliers=False, boxprops=dict(color="#481C48", edgecolor="black"))
		
	ax1 = sns.boxplot(x=tile_lane, y=tile_density_passed, showfliers=False, boxprops=dict(color="#EE533F", edgecolor="black"))
	for line in ax1.get_lines():
		line.set_color("black")
	
	fig.text(0.3, 0.01, "Cluster Density (Overall)", backgroundcolor="#481C48", color='white', size=15)
	fig.text(0.6, 0.01, "Cluster Density (Passed Filter)", backgroundcolor="#EE533F", color='white', size=15)
		
	ax1 = axFormatter(ax1)
	fig = figFormatter(fig)
	
	plt.ylim(0, max(tile_density)* 1.1)
	plt.ylabel("Cluster Density (k/mm2)", fontsize=20)
	plt.xlabel("Lane", fontsize=20)
	plt.title("Data by Lane: Cluster Density", fontsize=25)
	
	plt.savefig(os.path.join(inputString, "Interop_Images", "2_density_per_lane.jpg"), dpi = 200, bbox_inches = 'tight', pad_inches=0.25, edgecolor='black')
	
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
	
	plt.ylabel("Error Rate", fontsize=20)
	plt.xlabel("Cycle", fontsize=20)
	plt.title("Data by Cycle: Error Rate", fontsize=25)
	
	plt.savefig(os.path.join(inputString, "Interop_Images", "5_error_rate.jpg"), dpi = 200, bbox_inches = 'tight', pad_inches=0.25, edgecolor='black')
	
	plt.clf()
	
	return

def figFormatter(fig):

	fig.set_size_inches(18.5,10.5)
	
	return fig

def indexPercentRead( inputString ):

	run_folder = inputString
	
	run_metrics = py_interop_run_metrics.run_metrics()
	valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
	
	valid_to_load[py_interop_run.Index]=1
	
	run_metrics.read(run_folder, valid_to_load)
	run_summ = core.index_summary(run_folder, level="Barcode")
	
	#print(type(run_summ))
	run_masked = numpy.ma.array(run_summ, mask = [run_summ["Lane"] != 1])
	#print(run_masked)
	
	fig,ax = plt.subplots()
	sns.barplot(x=run_masked["Id"], y=run_masked["Fraction Mapped"], palette=miColor, edgecolor="black")
	
	plt.ylabel("% Reads Identified", fontsize=20)
	plt.xlabel("Index Number", fontsize=20)
	plt.title("% Reads Identified (PF) Per Index", fontsize=25)
	
	
	ax = axFormatter(ax)
	fig = figFormatter(fig)
	
	plt.savefig(os.path.join(inputString, "Interop_Images", "6_index_percent_read.jpg"), dpi = 200, bbox_inches = 'tight', edgecolor='black')
	plt.clf()
	
	return
	

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
				
		y = [bar_data.at(i).at(j).y() for j in range(bar_data.at(i).size())]
		w = [bar_data.at(i).at(j).width() for j in range(bar_data.at(i).size())]
		
		#print(x, y, w)
		
		xup, xdown = [], []
		yup, ydown = [], []
		wup, wdown = [], []
		
		if x:
			for index, x1 in enumerate(x):
				
				if x1 >= 30 and w[index] > 1.0:
					xup.append(x1)
					yup.append(y[index])
					wup.append(w[index])
				elif x1 < 30 and w[index] > 1.0:	
					xdown.append(x1)
					ydown.append(y[index]) 
					wdown.append(w[index])
		'''
		if bar_data.at(i).color() == "Blue":
			myColor = "#481C48"
		elif bar_data.at(i).color() == "DarkGreen":
			myColor = "#EE533F"
		else:
			myColor = "#E30B5D"
		'''
		ax.bar(xup, yup, width=wup, align="edge", color="#481C48", edgecolor='w')
		ax.bar(xdown, ydown, width=wdown, align="edge", color="#EE533F", edgecolor='w')
	    	#plt.text(x, y, str(y))

	ax = axFormatter(ax)
	fig = figFormatter(fig)
	
	plt.xlabel(bar_data.xyaxes().x().label(), fontsize=20)
	plt.ylabel(bar_data.xyaxes().y().label(), fontsize=20)
	plt.title("Q Score Distribution Chart", fontsize=25)
	plt.ylim([bar_data.xyaxes().y().min(), bar_data.xyaxes().y().max()])
	plt.xlim([bar_data.xyaxes().x().min(), bar_data.xyaxes().x().max()])
	
	
	plt.savefig(os.path.join(inputString, "Interop_Images", "1_qscore_histogram.jpg"), dpi = 200, bbox_inches = 'tight', pad_inches=0.25, edgecolor='black')
	
	plt.clf()
	
	return 

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
	#heatmap_ar[40,cols] = heatmap_floats[39]
	#print(heatmap_ar[40,cols])
		
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
	yrange = numpy.arange(0, 40, 0.125)
	
	ax = sns.heatmap(heatmap_matrix, yticklabels=yrange, cmap=miColor, cbar_kws={"label": '% of Max'})
	ax.tick_params(length=0)
	
	for index, label in enumerate(ax.yaxis.get_ticklabels()):
		if index % 32 != 0 and label != 100.0:
			label.set_visible(False)
	
	fig = figFormatter(fig)
	
	plt.xlabel(heatmap_data.xyaxes().x().label(), fontsize=20)
	plt.ylabel(heatmap_data.xyaxes().y().label(), fontsize=20)
	plt.title(heatmap_data.title() + ": Q-Score Heatmap", fontsize=25)
	plt.ylim([heatmap_data.xyaxes().y().min(), heatmap_data.xyaxes().y().max()*8])
	plt.xlim([heatmap_data.xyaxes().x().min(), heatmap_data.xyaxes().x().max()])
	plt.xticks(rotation=45)
	plt.text(-4, 317.5, "40.0", color='black')
	
	plt.savefig(os.path.join(inputString, "Interop_Images", "3_qscore_heatmap.jpg"), dpi = 200, bbox_inches = 'tight', pad_inches=0.25, edgecolor='black')
	plt.clf()
	
	return

def readSummary( inputString ):

	run_folder = inputString
	
	run_metrics = py_interop_run_metrics.run_metrics()
	valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
	
	valid_to_load[py_interop_run.Index]=1
	
	run_metrics.read(run_folder, valid_to_load)
	run_summ = core.summary(run_folder, level="Total")
	run_lane = core.summary(run_folder, level="Lane")
	run_read = core.summary(run_folder, level="Read")
	run_nonindex = core.summary(run_folder, leve='NonIndex')
	
	df_read = pd.DataFrame(run_read)
	df_read.drop("IsIndex", 1)
	#print(df_read)
	
	df_total = pd.DataFrame(run_summ)
	df_nonindex = pd.DataFrame(run_nonindex)
	
	html_read = df_read.to_html()
	#print(html)
	
	try:
		os.mkdir(os.path.join(inputString, "Interop_Images", "Summaries"))
	except:
		pass
	
	with open(os.path.join(inputString, "Interop_Images", "Summaries", "read_summary.html"), 'w') as outfile:
		outfile.write(html_read)
	
	df_lane = pd.DataFrame(run_lane)
	html_lane = df_lane.to_html()
	
	with open('/home/mecore/Desktop/timp/testing_ground/lane_summary.html', 'w') as outfile:
		outfile.write(html_lane)
		
	
	#print(run_nonindex.dtype)
	#print(run_lane.dtype)
	#print(run_read.dtype)
	#print(run_summ.dtype)

def interopGenerator(myRun):

	run_folder = myRun["Path"]
	
	try:
		os.mkdir(os.path.join(run_folder, "Interop_Images"))
	except:
		pass
	
	try:
		errorExtraction(run_folder)
	except:
		pass
		#print("error fail")
	
	try:
		indexPercentRead(run_folder)
	except:
		pass
		#print("index fail")
	
	try:
		basePercent(run_folder)
	except:
		pass
		#print("base fail")
	
	#try:
	densityPerLane(run_folder)
	#except:
	#	print("density fail")
	
	try:
		qscoreHistogramActual = qscoreHistogram(run_folder)
	except:
		pass
		#print("histo fail")
		
	try:
		qscoreHeatmapActual = qscoreHeatmap(run_folder)
	except:
		pass
		#print("heat fail")
	
	imageFolderLocation = os.path.join(run_folder, "Interop_Images")
	
	#try:
	readSummary(run_folder)
	#except:
		#pass
		#print
	'''
	try:
		OccupiedPerLane(run_folder)
	except:
		print("percentOccupiedPerLane failed")

	'''
	return imageFolderLocation

def main():
	
	subjectRunTest = {"Path": "/run/user/1000/gvfs/smb-share:server=bigbird.ibb.gatech.edu,share=ngs/NovaSeq/EH08/", "runName": "EH08", "runInstrument":"NovaSeq", "FlowcellID":"H5KWGDRXY", "outputFolderLocation":""}
	interopGenerator(subjectRunTest)
	
	return

main()
