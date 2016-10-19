#clear
#reset

#set terminal dumb

set xlabel ''
set ylabel 'Prediction Rate'
set ylabel offset 2.5,0

load 'include/histogram.gnu'
load 'include/palette.paired.gnu'

set style histogram clustered errorbars gap 2 title
#unset key
set key under nobox
set key samplen 1
set key width -3 maxrows 1
set xtics rotate by -45
set mytics 4
set yrange [0:100]
set format y "%3.0f\\%%"

set tmargin 0

plot	'data/prediction.csv' \
		using 'a_pred_rate_mean':(1.96*column('a_pred_rate_se')):xtic(1) title 'Average' ls 2, \
	''	using 'i_pred_rate_mean':(1.96*column('i_pred_rate_se')):xtic(1) title 'W. Average' ls 6, \
	''	using 'p_pred_rate_mean':(1.96*column('p_pred_rate_se')):xtic(1) title 'Previous' ls 4
    
	
set terminal epslatex size 3.30,1.5 color colortext
set output 'prediction.tex'
replot

