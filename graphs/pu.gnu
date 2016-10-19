set terminal wxt size 1024,768 persist raise

load 'include/histogram.gnu'
load 'include/palette.paired.gnu'

set key under nobox
set style histogram title offset 0,-1
set boxwidth 0.8 relative
set xlabel ""
set ylabel "Cycles"
set xtics rotate by -45

plot 'data/performance.csv' \
            u 'standard_mean':xtic(1) ls 2, \
        ''  u 'drowsy_mean' ls 6, \
        ''  u 'gated_mean' ls 4, \
        ''  u 'bayesian_mean' ls 8

