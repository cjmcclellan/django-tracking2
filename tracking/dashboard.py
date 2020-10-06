import dash_core_components as dcc
import dash_table
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_cjm.plots.BasicApp import BaseApp
import plotly.graph_objects as go
from django_plotly_dash import DjangoDash
from tracking.models import Visitor, Pageview
import numpy as np
import datetime


class TrackingDashboard(BaseApp):

    def __init__(self, django=True, *args, **kwargs):
        super(TrackingDashboard, self).__init__(django=django, *args, **kwargs)

        pageview_stats = Pageview.objects.stats()

        self.app.layout = html.Div(
            html.Div(
                [
                    dcc.Checklist(id='clear_bots',
                                  options=[
                                      {'label': 'No Bot Keyword', 'value': 'bot'},
                                      {'label': 'No Agent Keyword', 'value': 'agent'},
                                      {'label': 'No http Keyword', 'value': 'http'},
                                      {'label': 'No Trident Keyword', 'value': 'Trident'},

                                  ],
                                  value=['bot', 'agent', 'http', 'Trident']),
                    # html.Div(
                    #     [html.P('Filter Agents (use comma to separate inputs)'),
                    #      dcc.Input(id='remove_agents',
                    #                   options=[{'label': loc, 'value': loc} for loc in pageview_stats['geo_location'].keys()],
                    #                   multi=True)]
                    # ),
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        # min_date_allowed=dt(1995, 8, 5),
                        # max_date_allowed=dt(2017, 9, 19),
                        # initial_visible_month=dt(2017, 8, 5),
                        # end_date=dt(2017, 8, 25).date()
                    ),
                    html.Div(
                        [html.P('Remove Locations'),
                         dcc.Dropdown(id='remove_locations',
                                 options=[{'label': loc, 'value': loc} for loc in pageview_stats['geo_location'].keys()],
                                 multi=True)]
                    ),
                    html.Button('update', id='hidden_update'),
                    html.Div(id='geo_map'),


                    ]
            )
        )

        @self.app.callback(Output('geo_map', 'children'),
                           [Input('hidden_update', 'n_clicks')],
                           [State('clear_bots', 'value'), State('remove_locations', 'value'),
                            State('date-picker-range', 'start_date'), State('date-picker-range', 'end_date')])
        def update_graph(hidden_update, clear_bots, remove_locations, start_date, end_date):
            if end_date is None and start_date is not None:
                end_date = (datetime.datetime.strptime(start_date, '%Y-%m-%d') + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            pageview_stats = Pageview.objects.stats(start_date=start_date, end_date=end_date,
                                                    filter_agents=clear_bots, remove_locations=remove_locations)
            # a = 5
            fig = go.Figure()

            # now loop over every geo_location (execpt for None) and add that spot to the map
            location_amount = len(pageview_stats['geo_location'].keys())
            for location, location_stats in pageview_stats['geo_location'].items():
                if location is not 'None':
                    fig.add_trace(go.Scattergeo(
                        lat=[location_stats['lat']],
                        lon=[location_stats['lon']],
                        text=location + '<br> All Time Views: ' + str(location_stats['count']),
                        marker={'size': np.log(location_stats['count'])/np.log(location_amount) * 20,
                                'sizemode': 'area'},
                        showlegend=False
                    ))

            fig.update_layout(title_text='World Map of 2D Trends Ping Locations',
                              height=700)

            geo_map = dcc.Graph(figure=fig)

            # now create the table
            table = dash_table.DataTable(
                id='table',
                columns=[{'name': i, 'id': i} for i in pageview_stats['url_stats'][0]['visitors'][0].keys()],
                data=pageview_stats['url_stats'][0]['visitors'],
                style_table={'overflowX': 'auto'},
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                # column_selectable="single",
                row_selectable="multi",
                row_deletable=True,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=20,
            )

            stats = html.Div(['total count: {0}'.format(pageview_stats['url_stats'][0]['total_count']),
                              '   unique count: {0}'.format(pageview_stats['url_stats'][0]['unique_count'])])

            # add the daily views plot
            daily_views = dcc.Graph(figure=go.Figure([go.Scatter(x=list(pageview_stats['daily views'].keys()),
                                                                 y=list(pageview_stats['daily views'].values()))]))

            return [stats, geo_map, daily_views, table]
