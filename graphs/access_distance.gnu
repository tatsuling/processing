#clear
#reset

set terminal dumb

set xlabel "Cycles between accesses"
set ylabel "LLC Blocks"
set ylabel offset 2.5,0

load 'include/histogram.gnu'
load 'include/palette.const.gnu'


set logscale x 2
set format x "$2^{%L}$"
set format y "%3.0f\\%%"

set xrange [1:4294967296.]
set xtics border nomirror out scale default 1,16
set ytics border nomirror scale default 0,20
#set key under nobox
unset key

set tmargin 0

plot 	\
	'data/histogram.blackscholes.csv'	using "ii":(100*column("distance_mean")) with lines title "blackscholes" ls 1, \
	'data/histogram.bodytrack.csv'		using "ii":(100*column("distance_mean")) with lines title "bodytrack" ls 2, \
	'data/histogram.canneal.csv'		using "ii":(100*column("distance_mean")) with lines title "canneal" ls 3, \
	'data/histogram.dedup.csv'		    using "ii":(100*column("distance_mean")) with lines title "dedup" ls 4, \
	'data/histogram.ferret.csv'		    using "ii":(100*column("distance_mean")) with lines title "ferret" ls 5, \
	'data/histogram.fluidanimate.csv'	using "ii":(100*column("distance_mean")) with lines title "fluidanimate" ls 6, \
	'data/histogram.raytrace.csv'		using "ii":(100*column("distance_mean")) with lines title "raytrace" ls 7, \
	'data/histogram.swaptions.csv'		using "ii":(100*column("distance_mean")) with lines title "swaptions" ls 8, \
	'data/histogram.x264.csv'		    using "ii":(100*column("distance_mean")) with lines title "x264" ls 9

set label "$BET_{lp}$" at 2,70
set arrow from 16,60 to 554,25 head back nofilled ls 1
set arrow from 554,0 to 554,70 nohead ls 10

set label "$BET_{gated}$" at 5000,70
set arrow from 32000,60 to 611129,25 head back nofilled ls 1
set arrow from 611129,0 to 611129,70 nohead ls 10

set terminal epslatex size 3.30,1.10 color colortext
set output 'access_distance.tex'
replot
