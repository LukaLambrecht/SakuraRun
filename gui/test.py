####################################
# Attempt at more interactive plot #
####################################

import os
import sys
import requests
import numpy as np
import pandas as pd

# import plotly and dash
import dash
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Output, Input, State, callback, dcc, html

# set path for local imports
thisdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(thisdir, '..')))

# local imports
from python.distancematrix import get_distance_matrix
from python.distancematrix import plot_distance_matrix
from python.route import get_route_coords
from python.route import plot_route_coords
from tools.kmltools import coords_to_kml
from tools.tsptools import solve_tsp


def make_plot(df, highlight_idx=None, selected_ids=None):

    # add some plot info to df
    df['color'] = 'blue'
    df['size'] = 1
    df['idx'] = np.arange(len(df))

    # make highlight(s)
    if highlight_idx is not None:
        size = [1]*len(df)
        size[highlight_idx] = 2
        df['size'] = size
    if selected_ids is not None:
        color = ['blue']*len(df)
        for idx in selected_ids: color[idx] = 'red'
        df['color'] = color

    # set which attributes to display
    hover_data = {
        'idx': False, # note: "idx" must be the first item in order for callback to work,
                      #       since it relies on the ordering of "custom_data"...
                      #       to find cleaner way later.
        'size':False, 'color':False, 'lat':True, 'lon':True}

    # make basic plot
    fig = px.scatter_mapbox(df, lat="lat", lon="lon",
                color='color', color_discrete_map='identity',
                size='size', size_max=10,
                hover_data=hover_data,
                zoom=10, height=600, width=900)
    
    # plot aesthetic settings
    fig.update_layout(mapbox_style="open-street-map") # map style
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}) # margins
    fig.update_layout(uirevision=True) # persistent zoom level on updates
    return fig


class SakuraRunApp():

    def __init__(self, df):
        
        # initialize the app
        self.app = Dash()

        # initialize the map figure and related properties
        self.df = df.copy()
        self.selected_ids = list(range(len(self.df)))
        self.highlight_idx = None
        self.mapfig = self.make_map()

        # initialize other properties
        self.session = requests.Session()
        self.distance_matrix = None

        # define components
        self.titlediv = html.Div(children="Sakura Run")
        self.mapdiv = html.Div(
          [dcc.Graph(id='mapdiv', figure=self.mapfig)],
          style={'width': '75%', 'display': 'inline-block'}
        )
        self.distance_matrix_type_items = html.Div(
          [dcc.RadioItems(
              options={'full': 'Full', 'approx': 'Approx'},
              value='Full',
              id='distance_matrix_type_items')
          ]
        )
        self.distance_matrix_calc_button = html.Div(
          [html.Button('Calculate distance matrix',
              id='distance_matrix_calc_button',
              n_clicks=0),
          ]
        )
        self.distance_matrix_ready_div = html.Div(
            id='distance_matrix_ready_div',
            children='Distance matrix NOT set.'
        )
        self.route_calc_button = html.Div(
          [html.Button('Calculate shortest path',
              id='route_calc_button',
              n_clicks=0)
          ]
        )
        self.route_result_div = html.Div(
            id='route_result_div',
            children='Shortest path NOT calculated.'
        )

        # make layout
        self.app.layout = self.make_layout()

        # define callback for clicking on a map item
        @callback(
            Output(component_id='mapdiv', component_property='figure'),
            Input(component_id='mapdiv', component_property='clickData'),
            State('mapdiv', 'figure'),
            prevent_initial_call=True,
            allow_duplicate=True
        )
        def update_graph(clickData, f):
            if clickData is not None:
                # find which point was clicked
                idx = clickData['points'][0]['customdata'][0]
                # select or deselect chosen idx
                if idx in self.selected_ids: self.selected_ids.remove(idx)
                else: self.selected_ids.append(idx)
                # make a new figure
                self.mapfig = self.make_map()
                return self.mapfig
            return dash.no_update

        # define auxiliary callback for clicking on a map item
        @callback(
            Output(component_id='distance_matrix_ready_div', component_property='children',
                   allow_duplicate=True),
            Input(component_id='mapdiv', component_property='clickData'),
            prevent_initial_call=True,
        )
        def reset_distance_matrix_ready_div(clickData):
            if clickData is not None:
                self.distance_matrix = None
                return 'Distance matrix NOT set.'
            return dash.no_update

        # define auxiliary callback for clicking on a map item
        @callback(
            Output(component_id='route_result_div', component_property='children',
                   allow_duplicate=True),
            Input(component_id='mapdiv', component_property='clickData'),
            prevent_initial_call=True,
        )
        def reset_route_result_div(clickData):
            if clickData is not None:
                return 'Shortest path NOT calculated.'
            return dash.no_update

        # define callback for clicking on the calculate distance matrix button
        @callback(
            Output(component_id='distance_matrix_ready_div', component_property='children',
                   allow_duplicate=True),
            Input(component_id='distance_matrix_calc_button', component_property='n_clicks'),
            State(component_id='distance_matrix_type_items', component_property='value'),
            prevent_initial_call=True,
        )
        def calculate_distance_matrix(nclicks, value):

            # check state and set options
            geodesic = False
            if value=='full': pass
            elif value=='approx': geodesic = True
            else: raise Exception(f'Value "{value}" not recognized.')

            # get coordinates in suitable format
            lats = df["lat"].astype(float)
            lons = df["lon"].astype(float)
            coords = [{'lon': lon, 'lat': lat} for lon, lat in zip(lons, lats)]

            # select coordinates from currently selected indices
            coords = [coords[idx] for idx in self.selected_ids]

            # calculate distance matrix
            self.distance_matrix = get_distance_matrix(
              coords,
              session = self.session,
              #profile=args.profile,
              #blocksize=args.blocksize,
              geodesic = True # for testing
              #kmeans=args.kmeans_distance_matrix
            )

            # return informative state message
            msg = f'Distance matrix ready ({len(coords)} points, {value})'
            return msg

        # define callback for clicking on the calculate route button
        @callback(
            Output(component_id='route_result_div', component_property='children',
                   allow_duplicate=True),
            Input(component_id='route_calc_button', component_property='n_clicks'),
            prevent_initial_call=True,
        )
        def calculate_route(nclicks):
            if self.distance_matrix is None:
                msg = f'ERROR: cannot calculate route as distance matrix is not yet set.'
                return msg

            # optimization of route
            (ids, dist) = solve_tsp(self.distance_matrix, method='local')

            # todo: calculate actual route and plot

            msg = 'Shortest route: {:.3f} km'.format(dist/1000)
            return msg

    def make_map(self):
        # helper function of initializer to make the map figure
        figure = make_plot(
                   self.df,
                   highlight_idx=self.highlight_idx,
                   selected_ids=self.selected_ids)
        return figure

    def make_layout(self):
        # helper function of initializer to make layout
        layout = [
          self.titlediv,
          self.mapdiv,
          html.Hr(),
          self.distance_matrix_type_items,
          self.distance_matrix_calc_button,
          self.distance_matrix_ready_div,
          html.Hr(),
          self.route_calc_button,
          self.route_result_div,
          html.Hr()
        ]
        return layout


if __name__=='__main__':

    inputfile = sys.argv[1]
    dataset = pd.read_csv(inputfile)
    dataset['idx'] = np.arange(len(dataset))

    app = SakuraRunApp(dataset)
    app.app.run(port = 8059,
                debug = True,
                dev_tools_silence_routes_logging = False
    )
