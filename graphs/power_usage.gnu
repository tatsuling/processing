#set terminal wxt size 1024,768 persist raise

load 'include/histogram.gnu'
load 'include/palette.paired.gnu'

#set key inside right top nobox noopaque
set key outside right center vertical
set key box lw 2
set key invert
set key samplen 2
#set key spacing 1
#set key notitle
#set key noautotitles
#set key opaque
#set key width -10
#set key height 10
set style histogram rowstacked title offset 0,-1
set boxwidth 0.8 relative
set xlabel ""
set ylabel "Power Usage (W)"

# x2 axis labels
set x2tics axis in scale 0,0
set x2tics autojustify 
set x2tics offset first 1.5, character -1.25
set x2tics rotate by -30
set x2tics (    \
    'blackscholes' 0.0, \
    'bodytrack' 6.0, \
    'canneal' 12.0, \
    'dedup' 18.0, \
    'ferret' 24.0, \
    'fluidanimate' 30.0, \
    'raytrace' 36.0, \
    'swaptions' 42.0, \
    'x264' 48.0, \
    'Average' 54.0 \
)

set bmargin 6

plot newhistogram '', 'data/eu.blackscholes.csv' \
            u 'leakage_power_mean':xtic(1) ls 2 title 'Static', \
        ''  u 'dynamic_power_mean' ls 6 title 'Dynamic', \
        ''  u 'transition_power_mean' ls 4 title 'Transition', \
    newhistogram '', 'data/eu.bodytrack.csv' \
            u 'leakage_power_mean':xtic(1) ls 2 notitle 'Static', \
        ''  u 'dynamic_power_mean' ls 6 notitle 'Dynamic', \
        ''  u 'transition_power_mean' ls 4 notitle 'Transition', \
    newhistogram '', 'data/eu.canneal.csv' \
            u 'leakage_power_mean':xtic(1) ls 2 notitle 'Static', \
        ''  u 'dynamic_power_mean' ls 6 notitle 'Dynamic', \
        ''  u 'transition_power_mean' ls 4 notitle 'Transition', \
    newhistogram '', 'data/eu.dedup.csv' \
            u 'leakage_power_mean':xtic(1) ls 2 notitle 'Static', \
        ''  u 'dynamic_power_mean' ls 6 notitle 'Dynamic', \
        ''  u 'transition_power_mean' ls 4 notitle 'Transition', \
    newhistogram '', 'data/eu.ferret.csv' \
            u 'leakage_power_mean':xtic(1) ls 2 notitle 'Static', \
        ''  u 'dynamic_power_mean' ls 6 notitle 'Dynamic', \
        ''  u 'transition_power_mean' ls 4 notitle 'Transition', \
    newhistogram '', 'data/eu.fluidanimate.csv' \
            u 'leakage_power_mean':xtic(1) ls 2 notitle 'Static', \
        ''  u 'dynamic_power_mean' ls 6 notitle 'Dynamic', \
        ''  u 'transition_power_mean' ls 4 notitle 'Transition', \
    newhistogram '', 'data/eu.raytrace.csv' \
            u 'leakage_power_mean':xtic(1) ls 2 notitle 'Static', \
        ''  u 'dynamic_power_mean' ls 6 notitle 'Dynamic', \
        ''  u 'transition_power_mean' ls 4 notitle 'Transition', \
    newhistogram '', 'data/eu.swaptions.csv' \
            u 'leakage_power_mean':xtic(1) ls 2 notitle 'Static', \
        ''  u 'dynamic_power_mean' ls 6 notitle 'Dynamic', \
        ''  u 'transition_power_mean' ls 4 notitle 'Transition', \
    newhistogram '', 'data/eu.x264.csv' \
            u 'leakage_power_mean':xtic(1) ls 2 notitle 'Static', \
        ''  u 'dynamic_power_mean' ls 6 notitle 'Dynamic', \
        ''  u 'transition_power_mean' ls 4 notitle 'Transition', \
    newhistogram '', 'data/eu.Average.csv' \
            u 'leakage_power_mean':xtic(1) ls 2 notitle 'Static', \
        ''  u 'dynamic_power_mean' ls 6 notitle 'Dynamic', \
        ''  u 'transition_power_mean' ls 4 notitle 'Transition'

set terminal epslatex size 7.00,3.00 color colortext
set output 'power_usage.tex'

replot
