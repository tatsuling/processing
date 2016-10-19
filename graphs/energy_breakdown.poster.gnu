#set terminal wxt size 1024,768 persist raise
reset 

load 'include/histogram.gnu'
load 'include/palette.paired.gnu'

#set key outside right bottom vertical nobox invert
set key inside right top vertical nobox invert
set key opaque
set key at screen 0.7, screen 1.20
set key samplen 2
set key width -3
set style histogram rowstacked #title offset 0,-1
set boxwidth 0.8 relative
#set bmargin 6
set xlabel ""
set ylabel "Energy Breakdown (J)"

# x2 axis labels
set x2tics axis in scale 0,0
set x2tics center
#set x2tics offset 0, character -1.00
set x2tics (    \
    'blackscholes' 2.5, \
    'bodytrack' 8.5, \
    'canneal' 14.5, \
    'dedup' 20.5, \
    'ferret' 26.5, \
    'fluidanimate' 32.5, \
    'raytrace' 38.5, \
    'swaptions' 44.5, \
    'x264' 50.5, \
    'Average' 56.5 \
)
set x2tics tc rgbcolor '#000000'
set format y "%0.2f"

#set terminal pngcairo size 7.00,3.50 color
#set output 'energy_breakdown.poster.png'

plot newhistogram '', 'data/eu.blackscholes.csv' \
            u 'leakage_energy_mean':xtic(1) ls 2 title 'Static', \
        ''  u 'dynamic_energy_mean' ls 6 title 'Dynamic', \
        ''  u 'transition_energy_mean' ls 4 title 'Transition', \
    newhistogram '', 'data/eu.bodytrack.csv' \
            u 'leakage_energy_mean':xtic(1) ls 2 notitle 'Static', \
        ''  u 'dynamic_energy_mean' ls 6 notitle 'Dynamic', \
        ''  u 'transition_energy_mean' ls 4 notitle 'Transition', \
    newhistogram '', 'data/eu.canneal.csv' \
            u 'leakage_energy_mean':xtic(1) ls 2 notitle 'Static', \
        ''  u 'dynamic_energy_mean' ls 6 notitle 'Dynamic', \
        ''  u 'transition_energy_mean' ls 4 notitle 'Transition', \
    newhistogram '', 'data/eu.dedup.csv' \
            u 'leakage_energy_mean':xtic(1) ls 2 notitle 'Static', \
        ''  u 'dynamic_energy_mean' ls 6 notitle 'Dynamic', \
        ''  u 'transition_energy_mean' ls 4 notitle 'Transition', \
    newhistogram '', 'data/eu.ferret.csv' \
            u 'leakage_energy_mean':xtic(1) ls 2 notitle 'Static', \
        ''  u 'dynamic_energy_mean' ls 6 notitle 'Dynamic', \
        ''  u 'transition_energy_mean' ls 4 notitle 'Transition', \
    newhistogram '', 'data/eu.fluidanimate.csv' \
            u 'leakage_energy_mean':xtic(1) ls 2 notitle 'Static', \
        ''  u 'dynamic_energy_mean' ls 6 notitle 'Dynamic', \
        ''  u 'transition_energy_mean' ls 4 notitle 'Transition', \
    newhistogram '', 'data/eu.raytrace.csv' \
            u 'leakage_energy_mean':xtic(1) ls 2 notitle 'Static', \
        ''  u 'dynamic_energy_mean' ls 6 notitle 'Dynamic', \
        ''  u 'transition_energy_mean' ls 4 notitle 'Transition', \
    newhistogram '', 'data/eu.swaptions.csv' \
            u 'leakage_energy_mean':xtic(1) ls 2 notitle 'Static', \
        ''  u 'dynamic_energy_mean' ls 6 notitle 'Dynamic', \
        ''  u 'transition_energy_mean' ls 4 notitle 'Transition', \
    newhistogram '', 'data/eu.x264.csv' \
            u 'leakage_energy_mean':xtic(1) ls 2 notitle 'Static', \
        ''  u 'dynamic_energy_mean' ls 6 notitle 'Dynamic', \
        ''  u 'transition_energy_mean' ls 4 notitle 'Transition', \
    newhistogram '', 'data/eu.Average.csv' \
            u 'leakage_energy_mean':xtic(1) ls 2 notitle 'Static', \
        ''  u 'dynamic_energy_mean' ls 6 notitle 'Dynamic', \
        ''  u 'transition_energy_mean' ls 4 notitle 'Transition'

