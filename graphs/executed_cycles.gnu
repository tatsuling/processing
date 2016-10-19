#
set terminal wxt size 1024,768 persist raise

load 'include/histogram.gnu'
load 'include/palette.paired.gnu'

set key under nobox
set style histogram errorbars gap 2 title
set xlabel ""
set ylabel "Cycles"
set xtics rotate by -45

set style fill transparent solid 0.9 noborder

plot 'data/performance.csv' \
            u (column('standard_mean')/1000000):(1.96*column("standard_se")/1000000):xtic(1) ls 2, \
        ''  u (column('drowsy_mean')/1000000):(1.96*column("drowsy_se")/1000000):xtic(1) ls 6, \
        ''  u (column('gated_mean')/1000000):(1.96*column("gated_se")/1000000):xtic(1) ls 4, \
        ''  u (column('bayesian_mean')/1000000):(1.96*column("bayesian_se")/1000000):xtic(1) ls 8

