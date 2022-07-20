from os import name
import streamlit as st
from datetime import date, datetime
from streamlit.proto.Empty_pb2 import Empty
import yfinance as yf
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
import json
PAGE_CONFIG = {"page_title":"StkForecast.io","page_icon":"chart_with_upwards_trend","layout":"wide"}
st.set_page_config(**PAGE_CONFIG)
st.markdown("""
    <style>
      @import 'https://fonts.googleapis.com/css?family=Montserrat';
      
      section[data-testid="stSidebar"] > div {
      width: 19.5rem;}
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

      input[aria-autocomplete="list"]{
      color: Darkblue;
      font-variant: all-petite-caps;
      }
      
      input[aria-label="Select a date."] {
      color:Darkblue;
      font-family: 'Montserrat';
      font-size: 20px;
      font-variant: all-petite-caps;}

      div[data-baseweb="base-input"] input {
      color: Darkblue;
      font-family: 'Montserrat';
      font-size: 20px;
      font-variant: all-petite-caps;}

      .css-q1blxj{
      position: absolute;
      margin-top: -10px;
      transform: scale(0.5);
      right: 7%;}
      
      /*.css-1et7pe5{
      border: none;
      padding: 6px 20px;
      color: white;
      font-weight: bolder;
      background: #cbcbcb;
      border-radius: 40px;}*/
      
      .dashboard-title {
      font-size: 45px;}

      .header {
      font-size: 25px;}

      .sub-header {
      font-size: 15px;}
      
      section[tabindex="0"] .block-container{
      padding: 4rem 2rem 0 1rem;
      }

      .streamlit-expanderHeader{
      font-family: Montserrat;
      color: Darkblue;
      font-size: 17px;
      text-transform: uppercase;}

      .change_alert{
      align-self: center;
      font-variant: all-petite-caps;
      color: darkorange;
      font-size: 20px;
      animation: blink 1s linear infinite;}

      @keyframes blink{
      0%{opacity: 1;}
      50%{opacity: 0.4;}
      100%{opacity: 1;} }

      blockquote {
      color: darkblue;
      position: relative;
      margin: 5px auto;
      width: 400px;
      line-height: 27px;
      padding-left: 30px;
      border-left: 2px solid darkblue;}
      
      blockquote span {
        display: block;
        text-align: right;
        font-size: 24px;
        line-height: 40px;
        margin-top: 10px;
        text-transform: uppercase;}
      
      blockquote:hover p {
        opacity: 0.5;
        transition: opacity 0.2s ease;}

                                              /*Home styling*/
                                              /*Trending tickers*/

      table tr:nth-child(even) td{
      background:#dedede66;}

      table tr:nth-child(odd) td{
        background:#fff;}
      
      table {
        width: 100%}
      
      table thead tr {
        height: 40px;
        background: #36304a;}
      
      .table100-head th {
        font-family: Montserrat;
        color: #fff;
        border: 0;
        line-height: 1.2;
        font-weight: unset;}
      .column1{
        white-space: nowrap;}       
      .css-vba4y6 th, .css-vba4y6 td, .css-vba4y6 tr {
        border:0;}

                                                /*News feed*/
      .single-blog-post.post-style-2 {
        margin-bottom: 20px;
        height: 105px;
        text-decoration: none;
        transition: .2s}
      
      .news_container a:hover{background-color:whitesmoke;transform:scale(1.05)}

      .single-blog-post {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);}
      .d-flex {
        display: -webkit-box!important;
        display: flex!important;}
      .single-blog-post.post-style-2 .post-thumbnail {
        -webkit-box-flex: 0;
        flex: 0 0 125px;
        min-width: 125px;
        min-height: 100px;
        margin-right: 15px;}
      .single-blog-post .post-thumbnail img {
        width: 100%;
        height: 100%}
      .single-blog-post.post-style-2 .post-content {
        padding: 5px 30px 5px 5px;}
      .single-blog-post.post-style-2 .post-content p {
        color:black;
        font-weight:bold;
        margin-bottom: 10px;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;}
      .single-blog-post .post-content .post-meta p {
        margin-bottom: 0;
        font-size: 12px;
        color: #ff0000;
        line-height: 1.4;}
      .single-blog-post .post-content .post-meta p span {
        font-size: 12px;
        color: #8d8d8d;}
      tbody tr:hover{-webkit-text-stroke: medium;}
      
      @media (max-width: 1475px){
      .css-keje6w {min-width: calc(100% - 1.5rem);}
      .single-blog-post.post-style-2 .post-content {
        padding: 20px 0 5px 5px;}
      /*.single-blog-post.post-style-2 .post-thumbnail {
        min-width: 115px;
        height: auto}*/ }
    """,
        unsafe_allow_html=True,
    )
with open("trending_quote.json", "r") as fp:
  trending_quote = json.load(fp)
with open("news_feed.json", "r") as fp:
  news_feed = json.load(fp)
with open("tickers_list.json", "r") as fp:
  tickers_tuple = tuple(json.load(fp).values())

title_message = st.empty()

stocks = (f"SELECT","OTHER") + tickers_tuple
#stocks = (f"SELECT",'AAPL', 'GOOG', 'MSFT', 'GME',"BTC-USD","BAT-USD","OTHER")
selected_stock = st.sidebar.selectbox("Select your ticker symbol", stocks)

if selected_stock == "OTHER":
    other_selected_stock = st.sidebar.text_input("Enter a ticker")

START_DATE = st.sidebar.date_input("Start date",value= pd.to_datetime("2015-01-01"))
END_DATE = st.sidebar.date_input("End date",value= pd.to_datetime(date.today().strftime("%Y-%m-%d")))

predictable_vars = ("Open","High","Low","Close","Adj Close","Volume")
predicted_var = st.sidebar.selectbox("Predicted Variable", predictable_vars)

n_years = st.sidebar.slider("Years of predictions: ", 1, 5)
period = n_years * 365
button_col, status_col = st.sidebar.columns([0.5,1])
apply_button = button_col.button("Apply")
#status_changes = status_col.empty()

current_input = {"selected_stock": selected_stock,
                 "START_DATE": START_DATE,
                 "END_DATE": END_DATE,
                 "predicted_var":predicted_var,
                 "n_years": n_years}


#                                   ______________Loading_data______________
#@st.cache(suppress_st_warning=True)
def load_data(ticker, START_DATE, END_DATE):
    
    data = yf.download(ticker, START_DATE, END_DATE)
    data.reset_index(inplace=True)

    if len(data) == 0 :
        st.warning(f"No matching results for <{ticker.upper()}>")
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
    future = m.make_future_dataframe(periods=period)
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
      st.session_state.n_years = n_years

      st.session_state.data = data
      st.session_state.display = True


if st.session_state.display:
  title_message.markdown('<p class = "dashboard-title">Dashboard</p>',unsafe_allow_html=True)
  
  # Checking if anything has been changed and not been applied yet:
  # This is achieved by comparing the session_state of each input updated the last time the button
  # "apply" is pressed and the current input, which is changed whenever a user changes something.

  for k,v in st.session_state.items():
    if k in current_input.keys():
      if v != current_input[k]:
        #status_changes.text("changes pending!")
        status_col.markdown('<p class = "change_alert">changes pending!</p>',unsafe_allow_html = True)

  data = st.session_state.data
  display_plot_raw_data(data, st.session_state.last_ticker)
  forecast_process(predicted_var, st.session_state.last_ticker)

else:
  home_left, home_right = st.columns(2)
  title_message.markdown(
    '<p class = "dashboard-title" style = "font-size : 35px">Escryptock makes it the easiest way to forecast your asset.</p>',
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
          {"".join(["<tr><td class='column1'>{}</td><td class='column2'>{}</td><td class='column3'>{}<td class='column4'>{}</td></tr>".format(v["symbol"], v["currentPrice"], v["open"], v["volume"]) for v in trending_quote.values()])}
        </tbody>
      </table>
    """, unsafe_allow_html = True)

  home_right.markdown(f"""
    <h1 class="home_col_1_2_header">Latest news</h1>
    <div class="news_container">
      {"".join(["<a href='{}' class='single-blog-post post-style-2 d-flex'><div class='post-thumbnail'><img src='{}' alt='News banner'></div><div class='post-content'><p>{}</p><div class='post-meta'><p><span>{}</span> on <span>{}</span></p></div></div></a>".format(v["url"],v["banner_image"],v["title"],v["author"],v["time_published"]) for v in news_feed.values()])}
    </div>
    """, unsafe_allow_html = True)

  #st.markdown("<p>Awaiting for instructions...<br>Please choose a ticker symbol on the left and apply the changes to get started.</p>",
  # unsafe_allow_html = True)





#  st.markdown(
#    """
#    <blockquote>
#    <p>Although expectations of the future are supposed to be the driving force in the capital markets, those expectations are almost totally dominated by memories of the past. Ideas, once accepted, die hard.
#      <span>- Peter Bernstein</span>
#    </p>
#    </blockquote>
#    """,
#    unsafe_allow_html=True)
#   st.markdown("""<p class = "quote"><span class = "q_mark">“</span>Although expectations of the future are supposed to be the driving force in the capital markets, those expectations are almost totally dominated by memories of the past. Ideas, once accepted, die hard.<span class = "q_mark">”</span><span class = "author"><br>— Peter Bernstein —</span></p>""",
#     unsafe_allow_html=True)
#T5NJMEN0K7I9NZKJ
#url = 'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=BTC&topics=financial_markets&limit=8&apikey=T5NJMEN0K7I9NZKJ'
#url = "https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=CRYPTO:BTC&topics=financial_markets&limit=10&apikey=T5NJMEN0K7I9NZKJ"
#https://colorlib.com/wp/css3-table-templates/
#https://investexcel.net/all-yahoo-finance-stock-tickers/