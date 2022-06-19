from dash import Dash, html, dcc, Input, Output

from dash_extensions import Lottie       
import dash_bootstrap_components as dbc 
import plotly.express as px              
import pandas as pd                      
from datetime import date
import calendar
from wordcloud import WordCloud          


# Lottie by Emil - https://github.com/thedirtyfew/dash-extensions
url_connections = "https://assets9.lottiefiles.com/private_files/lf30_5ttqPi.json"
url_companies = "https://assets9.lottiefiles.com/packages/lf20_EzPrWM.json"
url_msg_in = "https://assets9.lottiefiles.com/packages/lf20_8wREpI.json"
url_msg_out = "https://assets2.lottiefiles.com/packages/lf20_Cc8Bpg.json"
options = dict(loop=True, autoplay=True, rendererSettings=dict(preserveAspectRatio='xMidYMid slice'))


# Import LinkedIn data from csv files 
# Connections dataframe
df_cnt = pd.read_csv('Connections.csv')
df_cnt["Connected On"] = pd.to_datetime(df_cnt["Connected On"])
df_cnt["month"] = df_cnt["Connected On"].dt.month
df_cnt["month"] = df_cnt["month"].apply(lambda x: calendar.month_abbr[x])

# Invitations dataframe
df_invite = pd.read_csv('Invitations.csv')
df_invite["Sent At"] = pd.to_datetime(df_invite["Sent At"])


# Bootstrap themes by Ann: https://hellodash.pythonanywhere.com/theme_explorer
app = Dash(__name__, 
            external_stylesheets=[dbc.themes.LUX],
            meta_tags=[{'name': 'viewport',
            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5'}]
            )

app.layout = dbc.Container([

    # FIRST ROW -----------------------------------
    dbc.Row([

        dbc.Col([
            dbc.Card([
                dbc.CardImg(src='/assets/linkedin-logo.png')
            ], className='mb-2'),
            dbc.Card([
                dbc.CardBody([
                    dbc.CardLink("Zaid Azim", target="_blank", href="http://zaidazim.tiu.co.in")
                ])
            ], className='mb-2'),
        ], xs=12, md=4, lg=3),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.DatePickerSingle(
                        id='my-date-picker-start',
                        date=date(2021, 1, 1),
                        className='ml-2'
                    ),
                    dcc.DatePickerSingle(
                        id='my-date-picker-end',
                        date=date(2022, 6, 15),
                        className='mb-2 ml-5'
                    ),
                ])
            ], color="info"),
        ], xs=12, md=8, lg=9),

    ], className='mb-2 mt-2', justify='center'),

    # SECOND ROW -----------------------------------
    dbc.Row([

        dbc.Col([
            dbc.Card([
                dbc.CardHeader(Lottie(options=options, width="67%", height="67%", url=url_connections)),
                dbc.CardBody([
                    html.H6('Connections'),
                    html.H2(id='content-connections', children="000")
                ], style={'textAlign': 'center'})
            ]),
        ], xs=12, md=6, lg=3, className='mb-2'),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader(Lottie(options=options, width="32%", height="32%", url=url_companies)),
                dbc.CardBody([
                    html.H6('Companies'),
                    html.H2(id='content-companies', children="000")
                ], style={'textAlign': 'center'})
            ]),
        ], xs=12, md=6, lg=3, className='mb-2'),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader(Lottie(options=options, width="25%", height="25%", url=url_msg_in)),
                dbc.CardBody([
                    html.H6('Invites received'),
                    html.H2(id='invitations-received', children="000")
                ], style={'textAlign': 'center'})
            ]),
        ], xs=12, md=6, lg=3, className='mb-2'),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader(Lottie(options=options, width="53%", height="53%", url=url_msg_out)),
                dbc.CardBody([
                    html.H6('Invites sent'),
                    html.H2(id='invitations-sent', children="000")
                ], style={'textAlign': 'center'})
            ]),
        ], xs=12, md=6, lg=3, className='mb-2')

    ], className='mb-2'),

    # THIRD ROW -----------------------------------------
    dbc.Row([

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='line-chart', figure={})
                ])
            ]),
        ], xs=12, md=6, className='mb-2'),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='wordcloud', figure={})
                ])
            ]),
        ], xs=12, md=6),

    ],className='mb-2'),

    dbc.Row([

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='bar-chart', figure={})
                ])
            ]),
        ], xs=12)

    ], className='mb-2'),
], fluid=True)


# Updating the number cards in second row ***********************
@app.callback(
    Output('content-connections', 'children'),
    Output('content-companies', 'children'),
    Output('invitations-received', 'children'),
    Output('invitations-sent', 'children'),
    Input('my-date-picker-start', 'date'),
    Input('my-date-picker-end', 'date')
)
def update_number_cards(start_date, end_date):
    # Connections
    dff_c = df_cnt.copy()
    dff_c = dff_c[(dff_c['Connected On'] >= start_date) & (dff_c['Connected On'] <= end_date)]
    num_connections = len(dff_c)
    num_companies = len(dff_c['Company'].unique())

    # Invitations
    dff_i = df_invite.copy()
    dff_i = dff_i[(dff_i['Sent At'] >= start_date) & (dff_i['Sent At'] <= end_date)]
    num_sent = len(dff_i[dff_i['Direction'] == 'OUTGOING'])
    num_received = len(dff_i[dff_i['Direction'] == 'INCOMING'])

    return num_connections, num_companies, num_received, num_sent


# Line Chart ****************************************************
@app.callback(
    Output('line-chart','figure'),
    Input('my-date-picker-start','date'),
    Input('my-date-picker-end','date'),
)
def update_line(start_date, end_date):
    dff = df_cnt.copy()
    dff = dff[(dff['Connected On']>=start_date) & (dff['Connected On']<=end_date)]
    dff = dff[["month"]].value_counts()
    dff = dff.to_frame()
    dff.reset_index(inplace=True)
    dff.rename(columns={0: 'Total connections'}, inplace=True)

    fig_line = px.line(dff, x='month', y='Total connections', template='ggplot2',
                  title="Total connections by month")
    fig_line.update_traces(mode="lines+markers", fill='tozeroy',line={'color':'blue'})
    fig_line.update_layout(margin=dict(l=20, r=20, t=30, b=20))

    return fig_line

# Wordcloud ******************************************************
@app.callback(
    Output('wordcloud','figure'),
    Input('my-date-picker-start','date'),
    Input('my-date-picker-end','date'),
)
def update_pie(start_date, end_date):
    dff = df_cnt.copy()
    dff = dff.Position[(dff['Connected On']>=start_date) & (dff['Connected On']<=end_date)].astype(str)

    my_wordcloud = WordCloud(
        background_color='white',
        height=275
    ).generate(' '.join(dff))

    fig_wordcloud = px.imshow(my_wordcloud, template='ggplot2',
                              title="Connections by position")
    fig_wordcloud.update_layout(margin=dict(l=20, r=20, t=30, b=20))
    fig_wordcloud.update_xaxes(visible=False)
    fig_wordcloud.update_yaxes(visible=False)

    return fig_wordcloud


# Bar Chart ******************************************************
@app.callback(
    Output('bar-chart','figure'),
    Input('my-date-picker-start','date'),
    Input('my-date-picker-end','date'),
)
def update_bar(start_date, end_date):
    dff = df_cnt.copy()
    dff = dff[(dff['Connected On']>=start_date) & (dff['Connected On']<=end_date)]

    dff = dff[["Company"]].value_counts().head(5)
    dff = dff.to_frame()
    dff.reset_index(inplace=True)
    dff.rename(columns={0:'Total connections'}, inplace=True)

    fig_bar = px.bar(dff, x='Total connections', y='Company', template='ggplot2', title="Top 5 companies where connections work", text=
    'Company')

    fig_bar.update_yaxes(showticklabels=False)

    fig_bar.update_layout(margin=dict(l=20, r=20, t=30, b=20))

    fig_bar.update_traces(marker_color='blue')

    return fig_bar



if __name__=='__main__':
    app.run_server(debug=True)