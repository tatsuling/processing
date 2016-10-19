set terminal wxt size 1024,768 persist raise

load 'include/histogram.gnu'
load 'include/palette.paired.gnu'

set key under nobox
set style histogram gap 2 title
set xlabel ""
set ylabel "Number of Runs"
set xtics rotate by -45

set style fill transparent solid 0.9 noborder

plot 'data/performance.csv' \
            u (column('standard_count')):xtic(1) ls 2, \
        ''  u (column('drowsy_count')):xtic(1) ls 6, \
        ''  u (column('gated_count')):xtic(1) ls 4, \
        ''  u (column('bayesian_count')):xtic(1) ls 8

