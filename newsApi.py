import requests
from datetime import datetime as dt
import json
import base64

def get_news():
	url = "https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics=financial_markets&apikey=T5NJMEN0K7I9NZKJ"
	try:
		r = requests.get(url)
	
		data = r.json()["feed"][:4]		
		count = 0
		news_dict = dict()
		for news in data:
			
			title = news["title"]
	
			try:
				author = news["authors"][0]
			except:
				author = "Published"
				
			time_str = news["time_published"]
			date = f"{time_str[:4]}/{time_str[4:6]}/{time_str[6:8]}"
			time = f"{time_str[9:11]}:{time_str[11:13]}"
			date_time = date + " " + time
			time_published = dt.strptime(date_time, '%Y/%m/%d %H:%M').strftime("%b %d, %Y at %I:%M %p")
		
			banner_image = news["banner_image"]
			if len(banner_image) == 0:
				with open("static/img/default_banner.jpg", "rb") as fp:
					contents = fp.read()
					data_url = base64.b64encode(contents).decode("utf-8")
				#banner_image = "static/img/default_banner.jpg"
				banner_image = f"data:image/gif;base64,{data_url}"

			url = news["url"]
				
			news_dict[count]= {"title":title, "author":author, "time_published":time_published,
				"banner_image":banner_image, "url":url}
			
			count+=1
		with open("static/json/news_feed_backup.json", "w") as fp:
			json.dump(news_dict, fp)
		return news_dict
	
	except:
		# Handle API rate limits, in case of reaching maximum api calls or other potentiel errors
		# An older json file containing the data will be returned
		with open("static/json/news_feed_backup.json", "r") as fp:
			return json.load(fp)