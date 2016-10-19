load 'include/histogram.gnu'
load 'include/palette.paired.gnu'

set xlabel ""
set ylabel "Energy Delay Product (J*s)"
set ylabel offset 2.5,-2.5

set style histogram errorbars gap 2 title
set key under nobox
set key samplen 2
set xtics rotate by -45
set mytics 2
set ytics in
set ytics 0.01

set tmargin 0

set terminal epslatex size 3.30,1.5 color colortext
set output 'edp.tex'

plot 'data/edp.csv' \
	    using (column("s_edp_mean")):(1.96*column("s_edp_se")):xtic(1) title "on-only" ls 2,	\
	''  using (column("d_edp_mean")):(1.96*column("d_edp_se")):xtic(1) title "lp-only" ls 6,	\
	''  using (column("g_edp_mean")):(1.96*column("g_edp_se")):xtic(1) title "gated-only" ls 4,	\
	''  using (column("b_p_edp_mean")):(1.96*column("b_p_edp_se")):xtic(1) title "combined" ls 8

#set terminal epslatex size 3.30,2.50 color colortext
#set output 'edp_normalized.tex'
#
#plot 'data/edp.csv' \
#	    using (100*column("s_edp_mean")/column("s_edp_mean")):(100*1.96*column("s_edp_se")/column("s_edp_mean")):xtic(1) title "Standard" ls 2,	\
#	''  using (100*column("d_edp_mean")/column("s_edp_mean")):(100*1.96*column("d_edp_se")/column("s_edp_mean")):xtic(1) title "Drowsy" ls 6,	\
#	''  using (100*column("g_edp_mean")/column("s_edp_mean")):(100*1.96*column("g_edp_se")/column("s_edp_mean")):xtic(1) title "Gated" ls 4,	\
#	''  using (100*column("b_p_edp_mean")/column("s_edp_mean")):(100*1.96*column("b_p_edp_se")/column("s_edp_mean")):xtic(1) title "Bayesian" ls 8
