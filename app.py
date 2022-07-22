import streamlit as st
from datetime import date#, datetime
import yfinance as yf
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
import json
from newsApi import get_news
from trendingApi import get_trend

PAGE_CONFIG = {"page_title":"Escryptoc.k.","page_icon":"chart_with_upwards_trend","layout":"wide"}
st.set_page_config(**PAGE_CONFIG)

with open("static/css/style.css", "r") as fp:
  st.markdown(f"<style>{fp.read()}</style>", unsafe_allow_html = True)
with open("static/json/tickers_list.json", "r") as fp:
  tickers_tuple = tuple(json.load(fp).values())


trending_quote = get_trend()
news_feed = get_news()

title_message = st.empty()

stocks = (f"SELECT","OTHER") + tickers_tuple
selected_stock = st.sidebar.selectbox("Select your ticker symbol", stocks)

if selected_stock == "OTHER":
    other_selected_stock = st.sidebar.text_input("Enter a ticker")

START_DATE = st.sidebar.date_input("Start date",value= pd.to_datetime("2015-01-01"))
END_DATE = st.sidebar.date_input("End date",value= pd.to_datetime(date.today().strftime("%Y-%m-%d")))

predictable_vars = ("Open","High","Low","Close","Adj Close","Volume")
predicted_var = st.sidebar.selectbox("Predicted Variable", predictable_vars)

periods = (7, 30, 90, 180, 365, 730, 1095, 1460, 1825)
forecast_period = st.sidebar.selectbox("How many days to predict? ", periods)

button_col, status_col = st.sidebar.columns([0.5,1])
apply_button = button_col.button("Apply")

current_input = {"selected_stock": selected_stock,
                 "START_DATE": START_DATE,
                 "END_DATE": END_DATE,
                 "predicted_var":predicted_var,
                 "forecast_period": forecast_period}


#                                   ______________Loading_data______________
@st.cache(suppress_st_warning=True)
def load_data(ticker, START_DATE, END_DATE):
    
    data = yf.download(ticker, START_DATE, END_DATE)
    data.reset_index(inplace=True)

    if len(data) == 0 :
        st.warning(f"No matching results for <{ticker.upper()}>, or may no longer be available on Yahoo Finance!")
        st.info("Tip: Try a valid symbol for relevant results.")
        return None
    st.session_state.last_ticker = ticker
    return data

#                                   ______________Display_raw_data_Plotting______________


def display_plot_raw_data(data, stock_crypto):
  with st.expander(f"Data history - {stock_crypto}", expanded = True):
    st.subheader("Raw data")
    st.write(data)
  
    st.subheader("Data visualization")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = data["Date"], y = data["Open"], name = "Stock_open"))
    fig.add_trace(go.Scatter(x = data["Date"], y = data["Close"], name = "Stock_close"))
    fig.layout.update(xaxis_title = "Time-line", yaxis_title = "Price", 
        xaxis_rangeslider_visible = True, margin=dict(l=0, r=0, t=50, b=50), width = 900, height = 550,
        font_family="Montserrat",
        font_color = "darkblue",
        font_size = 16)
    st.plotly_chart(fig)

#                                   ______________Forecast_data______________
def forecast_process(predicted_var, stock_crypto):
  with st.expander(f"Forecasting - {stock_crypto}", expanded = True):
    data_length = len(data)
    df_train = data[["Date", predicted_var]]
    df_train = df_train.rename(columns = {"Date":"ds", predicted_var :"y"})
    m = Prophet()
    m.fit(df_train)
    future = m.make_future_dataframe(periods=forecast_period)
    forecast = m.predict(future)
    st.header("Preview: Forecast Data")
    #st.markdown(f"Predicted Variable: {predicted_var}")
    st.markdown(f'<p class = "sub-header">Predicted Variable: {predicted_var}</p>',unsafe_allow_html=True)
    forecast_table_display_choices = ("All","Trend",predicted_var+"_lower",predicted_var+"_upper","Trend_lower",
    "Trend_upper","Additive_terms","Additive_terms_lower","Additive_terms_upper",
    "Weekly","Weekly_lower","Weekly_upper","Yearly","Yearly_lower","Yearly_upper")
    forecast_table_display = st.multiselect("Displayed features:",forecast_table_display_choices, default="All", help="Add additional features to view on the table below.")
    forecast_table_display_selected = ["Date", predicted_var]+[indice.lower() if indice != predicted_var else indice for indice in forecast_table_display]
    
    if 'all' in forecast_table_display_selected:
      st.write(forecast.rename(columns = {"ds": "Date","yhat": predicted_var, "yhat_lower": predicted_var.lower()+"_lower",
        "yhat_upper": predicted_var.lower()+"_upper"})[data_length:].drop(columns = ["multiplicative_terms", "multiplicative_terms_lower", "multiplicative_terms_upper"]).reset_index(drop = True))
    else:
      st.write(forecast.rename(columns = {"ds": "Date","yhat": predicted_var, "yhat_lower": predicted_var.lower()+"_lower",
        "yhat_upper": predicted_var.lower()+"_upper"})[forecast_table_display_selected][data_length:].reset_index(drop = True))                                    
    
    st.subheader("Forecast visualization")
    forecast_fig = plot_plotly(m, forecast)
    st.plotly_chart(forecast_fig) 
    st.subheader("Forecast components visualization")
    forecast_comp_fig = m.plot_components(forecast)
    st.write(forecast_comp_fig)

if "display" not in st.session_state:
  st.session_state.display = False

if apply_button:
  if (selected_stock == f"SELECT") or (selected_stock == "OTHER" and len(other_selected_stock.strip()) == 0):
    pass
  else:
    if selected_stock != "OTHER":
      data = load_data(selected_stock, START_DATE,END_DATE)
    else:
      data = load_data(other_selected_stock, START_DATE, END_DATE)

    if data is not None:
      st.session_state.selected_stock = selected_stock
      st.session_state.START_DATE = START_DATE
      st.session_state.END_DATE = END_DATE
      st.session_state.predicted_var = predicted_var
      st.session_state.forecast_period = forecast_period

      st.session_state.data = data
      st.session_state.display = True


if st.session_state.display:
  title_message.markdown('<p class = "dashboard-title">Dashboard</p>',unsafe_allow_html=True)
  
  # Checking if anything has been changed and not been applied yet:
  # This is achieved by comparing the session_state of each input updated the last time the button
  # "Apply" is pressed and the current input, which is changed whenever a user changes something.

  for k,v in st.session_state.items():
    if k in current_input.keys():
      if v != current_input[k]:
        status_col.markdown('<p class = "change_alert">changes pending!</p>',unsafe_allow_html = True)

  data = st.session_state.data
  display_plot_raw_data(data, st.session_state.last_ticker)
  forecast_process(predicted_var, st.session_state.last_ticker)

else:
  home_left, home_right = st.columns(2)

  title_message.markdown(
    '<p class = "dashboard-title"><span class = "app-name" style = "font-size : 35px">Escryptock</span> makes it the easiest way to forecast your asset!</p>',
    unsafe_allow_html=True)

  home_left.markdown(f"""
    <h1 class="home_col_1_2_header">Trending tickers</h1>
    <table>
        <thead>
          <tr class="table100-head">
            <th class="column1">Symbol</th>
            <th class="column2">Last Price</th>
            <th class="column3">Open</th>
            <th class="column4">Volume</th>
          </tr>
        </thead>
        <tbody>
          {"".join(["<tr><td class='column1'>{}</td><td >{}</td><td>{}<td>{}</td></tr>".format(v["symbol"], v["currentPrice"], v["open"], v["volume"]) for v in trending_quote.values()])}
        </tbody>
      </table>
    """, unsafe_allow_html = True)

  home_right.markdown(f"""
    <h1 class="home_col_1_2_header">Latest news</h1>
    <div class="news_container">
      {"".join(["<a href='{}' class='single-blog-post post-style-2 d-flex'><div class='post-thumbnail'><img src='{}' alt='News banner'></div><div class='post-content'><p>{}</p><div class='post-meta'><p><span>{}</span> on <span>{}, GMT</span></p></div></div></a>".format(v["url"],v["banner_image"],v["title"],v["author"],v["time_published"]) for v in news_feed.values()])}
    </div>
    """, unsafe_allow_html = True)

  st.info("To get started, please choose a ticker symbol on the left and apply the changes.")

#https://investexcel.net/all-yahoo-finance-stock-tickers/