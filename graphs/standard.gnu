#clear
#reset

set terminal dumb

set xlabel ''
set ylabel 'Total Energy'
set ylabel offset 2.5,0

load 'include/histogram.gnu'
load 'include/palette.paired.gnu'

set style histogram errorbars gap 2 title
set key under nobox
#set key inside right top
set key samplen 2
set xtics rotate by -45
set mytics 4
set yrange [0:100]

set tmargin 0

set format y "%3.0f\\%%"

plot	'data/eu.standard_l2.csv'						\
		using (100*column("percent_leakage_mean")):(100*1.96*column("percent_leakage_se")):xtic(1) title "Static" ls 2,	\
	''	using (100*column("percent_dynamic_mean")):(100*1.96*column("percent_dynamic_se")) title "Dynamic" ls 6 #, \
#	''	using (100*column("percent_transition_mean")):(100*1.96*column("percent_transition_se")) title "Transition" ls 4
	
set terminal epslatex size 3.30,1.5 color colortext
set output 'standard.tex'
replot

