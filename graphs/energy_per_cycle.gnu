s(x)=(445.329e-3/32768*x/2.4e9)
d(x)=(276.394e-3/32768*x/2.4e9 + 1.188693359375e-12)
g(x)=(13.0000e-3/32768*x/2.4e9 + 2.048e-9)
bet_drowsy=554
bet_gated=611129

load 'include/palette.paired.gnu'

set style line 12 lc rgb '#a0a0a0' lt 12 lw 2
set style line 13 lc rgb '#a0a0a0' lt 13 lw 1
set grid xtics ytics mytics back ls 12, ls 13

set style line 11 lc rgb '#808080' lt 1
set border 3 back ls 11
set tics nomirror

#set key inside left top vertical box lw 2
set key inside right bottom vertical box lw 2
set key opaque
set key width -3
#set key height 1
set key samplen 2

set terminal epslatex size 3.30,1.3 color colortext font ",10"
set output 'energy_per_cycle.tex'

set xlabel "Cycles"
set ylabel "Energy per Block"
set ylabel offset 2,0

set xtics border in scale 0,0 nomirror norotate
set xtics ('1' 1e0, '10' 1e1, '100' 1e2, '1K' 1e3, '10K' 1e4, '100K' 1e5, '1M' 1e6, '10M' 1e7, '100M' 1e8)
set xtics tc rgbcolor '#000000'

#set ytics format ""
#set ytics add ('0.003' 0.0031371086883544921875 0)
#set ytics add ('0.003' 0.0031371086883544921875 1)
#set format y "%3.0s %cJ"
set ytics ( \
    '1 $fJ$'        0.000000000000001, \
    '10 $fJ$'       0.00000000000001, \
    '0.1 $pJ$'      0.0000000000001, \
    '1 $pJ$'        0.000000000001, \
    '10 $pJ$'       0.00000000001, \
    '0.1 $nJ$'      0.0000000001, \
    '1 $nJ$'        0.000000001, \
    '10 $nJ$'       0.00000001, \
    '0.1 $\mu J$'   0.0000001, \
    '1 $\mu J$'     0.000001 \
)
set ytics tc rgbcolor '#000000'

set tmargin 0

set mytics 0

set style fill  transparent solid 0.50
set samples 1024*10

set xrange [1:100000000]
set yrange [1e-15:]

set logscale xy 10


#set arrow from bet_drowsy,0.1 to bet_drowsy,10000 nohead ls 10
#set arrow from bet_gated,0.1 to bet_gated,10000 nohead ls 10

plot \
    0 <= x && x <= bet_drowsy ? s(x) : 1/0 notitle with filledcurves x1 ls 2, \
    bet_drowsy <= x && x <= bet_gated ? d(x) : 1/0 notitle with filledcurves x1 ls 6, \
    bet_gated <= x ? g(x) : 1/0 notitle with filledcurves x1 ls 4, \
    s(x) title 'powered-on' with lines ls 2, \
    d(x) title 'low-power' with lines ls 6, \
    g(x) title 'power-gated' with lines ls 4
    

