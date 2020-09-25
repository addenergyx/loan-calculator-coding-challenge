# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 07:02:46 2020

@author: david
"""

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import dash_daq as daq
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from dash_extensions.callback import DashCallbackBlueprint
import plotly.express as px
from random import randint

external_stylesheets =['https://codepen.io/IvanNieto/pen/bRPJyb.css', dbc.themes.BOOTSTRAP, 
                       'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.13.0/css/all.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                meta_tags=[
                    { 'name':'viewport','content':'width=device-width, initial-scale=1, shrink-to-fit=no' }, ## Fixes media query not showing
                    {
                        'name':'description',
                        'content':'Simple Interest Loan Calculator created for the Coder Foundry coding challenge',
                    },
                    {
                        'name':'keywords',
                        'content':'Interest Loan Calculator',
                    },                        

                    {
                        'property':'og:image',
                        'content':'https://i.imgur.com/JJotzS2.jpg',
                    },
                    {
                        'name':'title',
                        'content':'Interest Loan Calculator',                    
                    }
                ]
            )

server = app.server

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        {%css%}
        {%favicon%}
    </head>
    <body>
        <div></div>
        {%app_entry%}
        <footer> 
          {%config%} 
          {%scripts%} 
          {%renderer%}
        </footer>
    </body>
</html>
'''

app.title = 'Interest Loan Calculator'

colours = {
            'remaining':'#1FDBB5',
            'principal':'#F54784',
            'interest':'#FFAC51'
          }

def format_amount(value):
    return '£{:,.2f}'.format(value)

def total_monthly_payment(amount, rate, length):
    return amount * (rate/1200)/(1-(1+rate/1200)**(-length))

def amortization(amount, rate, length):
    
    total_interest = 0
    tmp = total_monthly_payment(amount, rate, length)

    lis = []
    for a in range(1, length+1):

        ip = amount * (rate/1200)

        pp = tmp - ip

        amount -= pp 

        if amount < 0:
            amount = 0
        # tmp = tmp - pp # At end each month, Remaining Balance = Previous Remaining Balance - principal payments

        total_interest += ip

        lis.append([a, tmp, pp, ip, total_interest, amount])

    return pd.DataFrame(
        lis,
        columns=[
            'Month',
            'Payment',
            'Principal',
            'Interest',
            'Total Interest',
            'Balance',
        ],
    )

graph_card = [
                html.Div([            
                    dcc.Loading(
                        dcc.Graph(id='graphy')
                    )
                ], id='graph-block', hidden=True)
             ]

stats_card = [
                dbc.CardBody(
                    [
                        html.H2('Your Results'),
                        html.P('Monthly Repayment'),
                        html.Strong(html.P(id='monthly-repayment', className='result')),
                        html.P('Total Repayable'),
                        html.Strong(html.P(id='total-repayable', className='result')),
                        html.P('Total Interest'),
                        html.Strong(html.P(id='total-interest', className='result'))
                    ], className='stats'
                )
             ]

def build_table(df):
    return html.Div(
    [
        #Header
        html.Table([html.Tr([html.Th(col) for col in df.columns])]
        +
        #body
        [
            html.Tr(
                [
                    html.Td(
                        html.P(row.values[0], className='balances'), **{'data-label': 'Month'}
                    ),
                    html.Td(
                        html.P(format_amount(row.values[1]), className='balances'), **{'data-label': 'Payment'} 
                    ),
                    html.Td(
                        html.P(format_amount(row.values[2]), className='balances'), className='amount', **{'data-label': 'Principal'}
                    ),
                    html.Td(
                        html.P(format_amount(row.values[3]), className='balances'), className='amount', **{'data-label': 'Interest'}
                    ),
                    html.Td(
                        html.P(format_amount(row.values[4]), className='balances'), className='amount', **{'data-label': 'Total Interest'} 
                    ),
                    html.Td(
                        html.P(format_amount(row.values[5]), className='balances'), className='amount', **{'data-label': 'Balance'} 
                    ),
                ]) for i, row in df.iterrows()], className="hover-table amortization-table"
        ), 
    ], className='table-block', #style={"height": "100%", "overflowY": "scroll", "overflowX": "hidden"}, #className='large-2'
    )


def build_fig(df):
    
    # mini = int(min(data) - 5)
    # maxi = int(max(data) + 5)
    
    # print(mini, maxi)
    
    df = df.round(2)
    
    remaining = df['Total Interest']
    principal = df['Principal']
    interest = df['Balance']
    
    remaining_trace = go.Scatter(x=df['Month'], y=remaining,
            mode='lines',
            name='Remaining',
            line = {'color':colours['remaining'], 'shape': 'spline', 'smoothing': 1},
            fill='tozeroy'
            )

    principal_trace = go.Scatter(x=df['Month'], y=principal, 
            mode='lines',
            name='Principal',
            line = {'color': colours['principal'], 'shape': 'spline', 'smoothing': 1},
            fill='tozeroy',
            )
    
    interest_trace = go.Scatter(x=df['Month'], y=interest, 
            mode='lines',
            name='Interest',
            line = {'color': colours['interest'], 'shape': 'spline', 'smoothing': 1},
            fill='tozeroy',
            )
    
    data = [interest_trace, principal_trace, remaining_trace]
    
    layout = go.Layout(paper_bgcolor='rgba(0,0,0,0)',
               plot_bgcolor='rgba(0,0,0,0)',
                font={
                      #'family': 'Courier New, monospace',
                      #'size': 18,
                      'color': 'grey'
                      },
                xaxis={    
                    #'showgrid': False, # thin lines in the background
                    'zeroline': False, # thick line at x=0
                    #'visible': False,  # numbers below
                    #'tickmode':'linear',
                    #'autorange':False,
                    'gridcolor':'#393939'
                },                                                
                yaxis={
                    #'showgrid': False,
                    'zeroline': False,
                    'visible': False,
                },
                autosize=False,
                margin=dict(
                      l=0,
                      r=0,
                      b=2,
                      t=0,
                ),
            )

    fig = go.Figure(data=data, layout=layout)
    
    fig.update_layout(
        height=400,
        #width=300,
        hovermode='x',
        showlegend=False,
    )
    
    return fig

def build_card(title, colour):
    return html.Div(
        [
            dbc.Row(
                [
                    #dbc.Col(html.Span(className='fas fa-money-bill-wave icon', style={'color':colour}), className='d-flex justify-content-center icon-container', width=3), 
                    dbc.Col(
                        [
                            html.P(title.capitalize(), className='money')
                        ], className='d-flex justify-content-center text-center')
                ]
            ),
            dbc.Row(
                [
                    #dbc.Col(width=3),
                    dbc.Col(html.P(id=f'{title}-value'), className='d-flex justify-content-center text-center')
                ]
            ),
        ]
    )

app.config.suppress_callback_exceptions = True

body = html.Div(
            [
              dbc.Row(
                    [
                        ## Side Panel
                        dbc.Col(
                           [
                               html.H1('Interest Loan Calculator', style={'text-align':'center'}),
                              
                               html.Div(
                                   [
                                       dbc.Row([
                                            dbc.Col([
                                                html.P("Loan Amount (£)", className='balances'),
                                            ]),
                                            dbc.Col([dcc.Input(value=0, id='loan-amount', type='number', min="0")], className='text-right')
                                        ], className="align-items-center"),
                                       dbc.Row([ dbc.Col([dcc.Slider(id='loan-slider', min=0, max=250000, step=100)]),]),
                                       dbc.Row([
                                            dbc.Col([
                                                html.P("Term Length (Months)", className='balances'),
                                            ]),
                                            dbc.Col([
                                                dcc.Input(value=0, id='term-length', type='number', min="0"),
                                            ], className='text-right'),
                                        ], className="align-items-center"),
                                        dbc.Row([ dbc.Col([dcc.Slider(id='term-slider', min=0, max=120, step=1)]),]),
                                        dbc.Row([
                                            dbc.Col([
                                                html.P("Interest Rate (%)", className='balances'),
                                            ]),
                                            dbc.Col([
                                                dcc.Input(value=0, id='interest-rate', type='number', min="0"),
                                            ], className='text-right'),
                                        ], className="align-items-center"),
                                        dbc.Row([ dbc.Col([dcc.Slider(id='rate-slider', min=0, max=50, step=.1)]),]),
                                       
                                        html.Div(dbc.Row([ dbc.Col(dbc.Card(stats_card, className='summary-card stats-card'))]), hidden=True, id='statss' )
                                        
                                   ], id='user-inputs'
                               )
                              
                              
                           ], id='side-panel', width=12, lg=3
                        ),
                      
                       ## Main panel
                       dbc.Col(
                           [                      
                               dbc.Row(
                                   [
                                       dbc.Col(html.Div(graph_card, id='graph-card'), width=12),
                                       # dbc.Col(html.Div(dbc.Card(bf_card, className='summary-card'), id='bf-card'), width=12, md=6, lg=3),
                                       # dbc.Col(html.Div(dbc.Card(cal_card, className='summary-card'), id='calories-card'), width=12, md=6, lg=3),
                                       # dbc.Col(html.Div(dbc.Card(act_card, className='summary-card'), id='activity-card'), width=12, md=6, lg=3),
                                       html.P(id='aaa')
                                   ], className = 'data-row'
                               ),
                               
                               html.Div([
                                   dbc.Row(
                                       [
                                           dbc.Col(build_card('remaining', colours['remaining']), width=4),
                                           dbc.Col(build_card('principal', colours['principal']), width=4),
                                           dbc.Col(build_card('interest', colours['interest']), width=4),
    
                                       ], className='data-row'
                                   ),
                               ], id='stats-block', hidden=True),
                               
                               dbc.Row(
                                   [
                                       dbc.Col(dbc.Card(id='full-data-card', className='summary-card'), width=12, lg=8),
                                       dbc.Col(dbc.Card(html.P(id='advice'), id='side-data-card', className='summary-card justify-content-center align-self-center'), width=12, lg=4),
                                       # dbc.Col(dbc.Card(stats_card, id='side-data-card', className='summary-card'), width=12, lg=4),
                                       # #dbc.Col(dbc.Card(aaa, id='test', className='summary-card'), width=12, lg=4),
                                   ], className = 'data-row'
                               ),
                                                    
                               dbc.Row(
                                   [
                                       dbc.Col(width=12),
                                   ], className = 'data-row'
                               ),
                                                    
                               # dcc.Interval(id="weight-interval", n_intervals=0, interval=60000),
                              
                           ], id='main-panel', width=12, lg=8
                     )
                ], no_gutters=True),
                dcc.Store(id="sync"),
                dcc.Store(id="sync2"),
                dcc.Store(id="sync3")

             ])

## https://community.plotly.com/t/synchronize-components-bidirectionally/14158/11

# Create callbacks.
dcb = DashCallbackBlueprint()

@dcb.callback(Output("sync", "data"), [Input("loan-amount", "value")])
def sync_input_value(value):
    return value

@dcb.callback(Output("sync", "data"), [Input("loan-slider", "value")])
def sync_slider_value(value):
    return value

@dcb.callback([Output("loan-amount", "value"), Output("loan-slider", "value")], [Input("sync", "data")],
              [State("loan-amount", "value"), State("loan-slider", "value")])
def update_components(current_value, input_prev, slider_prev):
    # Update only inputs that are out of sync (this step "breaks" the circular dependency).
    input_value = current_value if current_value != input_prev else dash.no_update
    slider_value = current_value if current_value != slider_prev else dash.no_update
    return [input_value, slider_value]



@dcb.callback(Output("sync2", "data"), [Input("term-length", "value")])
def sync_term_input_value(value):
    return value

@dcb.callback(Output("sync2", "data"), [Input("term-slider", "value")])
def sync_term_slider_value(value):
    return value

@dcb.callback([Output("term-length", "value"), Output("term-slider", "value")], [Input("sync2", "data")],
              [State("term-length", "value"), State("term-slider", "value")])
def update_term_components(current_value, input_prev, slider_prev):
    # Update only inputs that are out of sync (this step "breaks" the circular dependency).
    input_value = current_value if current_value != input_prev else dash.no_update
    slider_value = current_value if current_value != slider_prev else dash.no_update
    return [input_value, slider_value]



@dcb.callback(Output("sync3", "data"), [Input("interest-rate", "value")])
def sync_rate_input_value(value):
    return value

@dcb.callback(Output("sync3", "data"), [Input("rate-slider", "value")])
def sync_rate_slider_value(value):
    return value

@dcb.callback([Output("interest-rate", "value"), Output("rate-slider", "value")], [Input("sync3", "data")],
              [State("interest-rate", "value"), State("rate-slider", "value")])
def update_rate_components(current_value, input_prev, slider_prev):
    # Update only inputs that are out of sync (this step "breaks" the circular dependency).
    input_value = current_value if current_value != input_prev else dash.no_update
    slider_value = current_value if current_value != slider_prev else dash.no_update
    return [input_value, slider_value]

dcb.register(app)

# @app.callback(
#     Output('loan-amount', 'value'),
#     [Input('loan-slider', 'value')])
# def update_loan_box(value):
#     return value

# @app.callback(
#     Output('loan-slider', 'value'),
#     [Input('loan-amount', 'value')])
# def update_loan_slider(value):
#     return value


# @app.callback(
#     Output('term-length', 'value'),
#     [Input('term-slider', 'value')])
# def update_term_box(value):
#     return value

# @app.callback(
#     Output('term-slider', 'value'),
#     [Input('term-length', 'value')])
# def term_term_slider(value):
#     return value

# @app.callback(
#     Output('interest-rate', 'value'),
#     [Input('rate-slider', 'value')])
# def update_rate_box(value):
#     return value

# @app.callback(
#     Output('rate-slider', 'value'),
#     [Input('interest-rate', 'value')])
# def update_rate_slider(value):
#     return value

def format_value(num):
    return float('{:0.2f}'.format(num))

@app.callback([Output("remaining-value", "children"), Output("principal-value", "children"), 
               Output("interest-value", "children"), Output('stats-block','hidden')], 
              [Input("graphy", "clickData")])
def event_cb(data):
    
    # value_dict = {}
    
    # traces = ['interest', 'principal', 'remaining']
    
    # #row = data['points'][0]
    
    # for row, trace in zip(data['points'], traces):
    #     value_dict[trace] = row['y']
        
    return format_amount(data['points'][0]['y']), format_amount(data['points'][1]['y']), format_amount(data['points'][2]['y']), False

def advice(length2, savings):
    return [
            'If you decreased your term length to ',
            html.Span(length2, className='info'),
            ' you would save ',
            html.Span(format_amount(savings), className='info'), 
            ' in interest!!!'
           ]

@app.callback(
    [Output('graph-block', 'hidden'), Output('graphy', 'figure'), Output('statss', 'hidden'), 
     Output('monthly-repayment', 'children'), Output('total-repayable', 'children'),
     Output('total-interest', 'children'), Output('full-data-card','children'), 
     Output('advice', 'children')], 
    [Input('loan-amount', 'value'), Input('interest-rate', 'value'), Input('term-length', 'value')])
def update_slider(amount, rate, length):
    # if 0 in (amount, rate, length) or None in (amount, rate, length):
    #     pass
    # else:
    # amount = 1000         
    # rate = 3.9
    # length = 12
    # try:
    tmp = total_monthly_payment(amount, rate, length)
    # except ZeroDivisionError:
    #     return True, build_fig(df), False, format_amount(tmp), format_amount(principal_interest), format_amount(df['Total Interest'].iloc[-1]), build_table(df), guide

    df = amortization(amount, rate, length)
        
    principal_interest = amount + df['Total Interest'].iloc[-1]
        
    if length > 6:
        length2 =  randint(round(length/4), length-1)
        df2 = amortization(amount, rate, length2)
        savings = df['Total Interest'].iloc[-1] - df2['Total Interest'].iloc[-1]
        guide = advice(length2, savings)
    elif length > 1:
        length2 =  length - 1
        df2 = amortization(amount, rate, length2)
        savings = df['Total Interest'].iloc[-1] - df2['Total Interest'].iloc[-1]
        guide = advice(length2, savings)
    else:
        guide = 'Hi there!! Enter some details so we can calculate your loan payment.'
    
    return False, build_fig(df), False, format_amount(tmp), format_amount(principal_interest), format_amount(df['Total Interest'].iloc[-1]), build_table(df), guide

def button():
    return html.Div([dbc.Button([html.Span(className='fab fa-github icon')], className='fixed-btn', href='https://github.com/addenergyx/cf-coding-challenge', external_link=True)], className='button-container')

def Homepage():
    return html.Div([
            body,
            button()
        ], id='background')

"""
Set layout to be a function so that for each new page load                                                                                                       
the layout is re-created with the current data, otherwise they will see                                                                                                     
data that was generated when the Dash app was first initialised
"""     

#app.scripts.config.serve_locally=True
app.layout = Homepage()

if __name__ == '__main__':
    #app.run_server(debug=True, use_reloader=False)
    app.run_server()

















