#set terminal wxt size 1024,768 persist raise

load 'include/histogram.gnu'
load 'include/palette.paired.gnu'

set terminal epslatex size 3.30,1.75 color colortext
set output 'ipc.tex'

set style histogram errorbars gap 2 title
set key under nobox
set key samplen 2
set xtics rotate by -45
set mytics 2
set xlabel ""
set ylabel "Instructions/Cycle/Core"
set ylabel offset 2.5,0

set tmargin 0

plot 'data/ipc.csv' \
	    using (column("s_ipc_mean")/16):(1.96*column("s_ipc_se")/16):xtic(1) title "on-only" ls 2,	\
	''  using (column("d_ipc_mean")/16):(1.96*column("d_ipc_se")/16):xtic(1) title "lp-only" ls 6,	\
	''  using (column("g_ipc_mean")/16):(1.96*column("g_ipc_se")/16):xtic(1) title "gated-only" ls 4,	\
	''  using (column("b_p_ipc_mean")/16):(1.96*column("b_p_ipc_se")/16):xtic(1) title "combined" ls 8


reset
load 'include/histogram.gnu'
load 'include/palette.paired.gnu'

set terminal epslatex size 3.30,2.50 color colortext
set output 'ipc_normalized.tex'

set style histogram errorbars gap 2 title
set key under nobox
set xtics rotate by -45
set xlabel ""
set ylabel "Relative IPC"
plot 'data/ipc.csv' \
	    using (column("s_ipc_mean")/column("s_ipc_mean")):(column("s_ipc_se")/column("s_ipc_mean")):xtic(1) title "on-only" ls 2,	\
	''  using (column("d_ipc_mean")/column("s_ipc_mean")):(column("d_ipc_se")/column("s_ipc_mean")):xtic(1) title "lp-only" ls 6,	\
	''  using (column("g_ipc_mean")/column("s_ipc_mean")):(column("g_ipc_se")/column("s_ipc_mean")):xtic(1) title "gated-only" ls 4,	\
	''  using (column("b_p_ipc_mean")/column("s_ipc_mean")):(column("b_p_ipc_se")/column("s_ipc_mean")):xtic(1) title "combined" ls 8


#reset
#load 'histogram.gnu'
#load 'palette.paired.gnu'
#
#set terminal epslatex size 3.30,2.50 color colortext
#set output 'ipc_per_watt.tex'
#
#set style histogram errorbars gap 2 title
#set key under nobox
#set xtics rotate by -45
#set ylabel "IPC/Watt"
##set ytics 0.2
#plot 'data/ipc.csv' \
	    #using (column("s_ipc_per_watt_mean")):(1.96*column("s_ipc_per_watt_se")):xtic(1) title "Standard" ls 2,	\
	#''  using (column("d_ipc_per_watt_mean")):(1.96*column("d_ipc_per_watt_se")):xtic(1) title "Drowsy" ls 6,	\
	#''  using (column("g_ipc_per_watt_mean")):(1.96*column("g_ipc_per_watt_se")):xtic(1) title "Gated" ls 4,	\
	#''  using (column("b_ipc_per_watt_mean")):(1.96*column("b_ipc_per_watt_se")):xtic(1) title "Bayesian" ls 8

