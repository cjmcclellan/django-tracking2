from django.test import TestCase
from dash_cjm.plots.Plotting2DApp import StaticPlotting2DApp

# Create your tests here.
if __name__ == '__main__':
    plot = StaticPlotting2DApp(name='tracking_time', y_variables=['number'], x_variables=['time'],
                               compute_function=lambda x: {'number': [0, 1], 'time': [7, 8]}, django=False, class_name='None')

    plot.build_app()
    plot.app.run_server(debug=True)