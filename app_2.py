from os import name
import streamlit as st
from datetime import date, datetime
from streamlit.proto.Empty_pb2 import Empty
import yfinance as yf
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go

PAGE_CONFIG = {"page_title":"StkForecast.io","page_icon":"chart_with_upwards_trend","layout":"wide"}
st.set_page_config(**PAGE_CONFIG)
st.markdown("""
    <style>
      @import 'https://fonts.googleapis.com/css?family=Montserrat';
      
      *{
      font-family: 'Montserrat';
      color: Darkblue;
      font-size: 20px;}

      html,body,[class*="css"] {
      font-family: 'Montserrat';
      /*font-size: 14px;*/}
      
      div[aria-selected="true"] {
      font-variant: all-petite-caps;}
      
      li[role="option"] {
      font-variant: all-small-caps;}
      
      input[aria-label="Select a date."] {
      color:Darkblue;
      font-family: 'Montserrat';
      font-size: 20px;
      font-variant: all-petite-caps;}

      .css-q1blxj{
      position: absolute;
      margin-top: -10px;
      transform: scale(0.5);
      right: 7%;}
      
      .css-1et7pe5{
      border: none;
      padding: 6px 20px;
      color: white;
      font-weight: bolder;
      background: #cbcbcb;
      border-radius: 40px;}
      
      .dashboard-title {
      font-size: 45px;}

      .header {
      font-size: 25px;}

      .sub-header {
      font-size: 15px;}
    </style>
    """,
        unsafe_allow_html=True,
    )

st.markdown(f'<p class = "dashboard-title">Dashboard</p>',unsafe_allow_html=True)

col1, col2 = st.sidebar.columns([3, 0.1])

algo_approach = ("PROPHET",'LSTM', 'ARIMA')
algo_approach = col1.selectbox("Select the technique for forecasting", algo_approach)
info = col2.button("i")
stocks = (f"SELECT",'AAPL', 'GOOG', 'MSFT', 'GME',"BTC-USD","BAT-USD","OTHER")
selected_stock = st.sidebar.selectbox("Select your ticker symbol", stocks)

if selected_stock == "OTHER":
    other_selected_stock = st.sidebar.text_input("Enter the ticker:")

START_DATE = st.sidebar.date_input("Start date",value= pd.to_datetime("2015-01-01"))
END_DATE = st.sidebar.date_input("End date",value= pd.to_datetime(date.today().strftime("%Y-%m-%d")))

predictable_vars = ("Open","High","Low","Close","Adj Close","Volume")
predicted_var = st.sidebar.selectbox("Predicted Variable", predictable_vars)

n_years = st.sidebar.slider("Years of predictions: ", 1, 5)
period = n_years * 365

#                                   ______________Loading_data______________

@st.cache(suppress_st_warning=True)
def load_data(ticker):
    
    data = yf.download(ticker, START_DATE, END_DATE)
    data.reset_index(inplace=True)
    
    if len(data) == 0 :
        st.warning("There is no such stock ticker.")
        return None
    return data

if selected_stock == f"SELECT" or (selected_stock == "OTHER" and len(other_selected_stock.strip()) == 0):
  st.text("Awaiting for instructions...\nPlease choose the stock symbol on the left for further manipulations.")

else :
  if selected_stock == "OTHER" and len(other_selected_stock.strip()) != 0:
      data = load_data(other_selected_stock)
      
  elif selected_stock in stocks and selected_stock not in [f"SELECT", "OTHER"]:
      data = load_data(selected_stock)
        


#                                   ______________Display_raw_data_Plotting______________


def display_plot_raw_data():
  if data is not None:
      st.subheader("Raw data")
      st.write(data)
  else:
      pass

  st.subheader("Raw data visualization")
  fig = go.Figure()
  fig.add_trace(go.Scatter(x = data["Date"], y = data["Open"], name = "Stock_open"))
  fig.add_trace(go.Scatter(x = data["Date"], y = data["Close"], name = "Stock_close"))
  #fig.add_trace(go.Scatter(x = data["Date"], y = data["Adj Close"], name = "Adj Close"))
  fig.layout.update(title = "Historic data visualization", xaxis_title = "Time-line", yaxis_title = "Price", 
      xaxis_rangeslider_visible = True, margin=dict(l=0, r=0, t=50, b=50), width = 900, height = 550,
      font_family="Montserrat",
      font_color = "darkblue",
      font_size = 16)
  st.plotly_chart(fig)

#                                   ______________Forecast_data______________
def forecast_process(predicted_var):
  data_length = len(data)
  if algo_approach == "PROPHET":
    df_train = data[["Date", predicted_var]]
    df_train = df_train.rename(columns = {"Date":"ds", predicted_var :"y"})
    m = Prophet()
    m.fit(df_train)
    future = m.make_future_dataframe(periods=period)
    forecast = m.predict(future)
    st.header("Preview: Forecast Data")
    st.subheader(f"Predicted Variable: {predicted_var}")
    forecast_table_display_choices = ("All","Trend",predicted_var+"_lower",predicted_var+"_upper","Trend_lower",
                              "Trend_upper","Additive_terms","Additive_terms_lower","Additive_terms_upper",
                              "Weekly","Weekly_lower","Weekly_upper","Yearly","Yearly_lower","Yearly_upper")
    forecast_table_display = st.multiselect("Displayed indices",forecast_table_display_choices)
    forecast_table_display_selected = ["Date", predicted_var]+[indice.lower() if indice != predicted_var else indice for indice in forecast_table_display]

    if 'all' in forecast_table_display_selected:
      forecast_table_display = forecast_table_display_selected
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
  
  if algo_approach == "LSTM":
    st.title("LSTM technique under construction...")

  if algo_approach == "ARIMA":
    st.title("ARIMA technique under construction...")


if selected_stock != f"SELECT":
  if selected_stock == "OTHER" and len(other_selected_stock.strip()) == 0:
    pass
  else:
    if data is not None:
      try:
        display_plot_raw_data()
        forecast_process(predicted_var)
      except:
        pass