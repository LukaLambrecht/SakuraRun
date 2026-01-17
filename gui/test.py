####################################
# Attempt at more interactive plot #
####################################

import os
import sys
import numpy as np
import pandas as pd

# import plotly and dash
import dash
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Output, Input, State, callback, dcc, html


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

def make_app(df):

    # parse the input dataframe
    df['idx'] = np.arange(len(df))

    # initialize the app
    app = Dash()

    # make the figure
    selected_ids = list(range(len(df)))
    figure = make_plot(df, selected_ids=selected_ids)

    # make layout
    app.layout = html.Div([
      html.Div(
        [dcc.Graph(id='map_plot', figure=figure)],
        style={'width': '75%', 'display': 'inline-block'}
      ),
    ])

    # define callback
    @callback(
        Output(component_id='map_plot', component_property='figure'),
        Input(component_id='map_plot', component_property='clickData'),
        State('map_plot', 'figure'),
        prevent_initial_call=True
    )
    def update_graph(clickData, f):
        if clickData:
            # find which point was clicked
            idx = clickData['points'][0]['customdata'][0]
            # select or deselect chosen idx
            if idx in selected_ids: selected_ids.remove(idx)
            else: selected_ids.append(idx)
            # make a new figure
            fig = make_plot(df, highlight_idx=idx, selected_ids=selected_ids)
            return fig
        return dash.no_update

    return app


if __name__=='__main__':

    inputfile = sys.argv[1]
    dataset = pd.read_csv(inputfile)

    #fig = make_plot(dataset, highlight_idx=5, selected_ids=[7,5,3])
    #fig.show()

    app = make_app(dataset)
    app.run(port = 8059,
            debug = False,
            dev_tools_silence_routes_logging = True
    )
