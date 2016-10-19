#clear
#reset

#set terminal dumb

load 'include/histogram.gnu'
load 'include/palette.paired.gnu'

set xlabel ""
set ylabel "Relative Execution Time" 
set ylabel offset 2.5,-1.5

set style histogram errorbars gap 2 title  offset 0, 0, 0
set key under nobox
set key samplen 2
# set nokey
set xtics rotate by -45
set mytics 2

set tmargin 0

#set lmargin 5

plot 'data/performance.csv' \
	    using (column("standard_mean")/column('standard_mean')):(1.96*column("standard_se")/column('standard_mean')):xtic(1) title "on-only" ls 2,	\
	''  using (column("drowsy_mean")/column('standard_mean')):(1.96*column("drowsy_se")/column('standard_mean')):xtic(1) title "lp-only" ls 6,	\
	''  using (column("gated_mean")/column('standard_mean')):(1.96*column("gated_se")/column('standard_mean')):xtic(1) title "gated-only" ls 4,	\
	''  using (column("bayesian-prev_mean")/column('standard_mean')):(1.96*column("bayesian-prev_se")/column('standard_mean')):xtic(1) title "combined" ls 8

set terminal epslatex size 3.30,1.75 color colortext
set output 'performance.tex'
replot


