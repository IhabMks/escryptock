import json
import requests
from numerize import numerize

def get_trend():
	trend_url = 'https://yfapi.net/v1/finance/trending/US'
	
	headers = {
	    'x-api-key': "w91MQpwKdp4eYoT3mVhhf5DGsLMy7mBEznzKy6h1"
	    }
	try:
		response = requests.request("GET", trend_url, headers=headers)
	
		trend_dict = dict()

		trending_list = []
		trending_container = response.json()["finance"]["result"][0]["quotes"][:10]
		for symbol in trending_container:
			trending_list.append(symbol["symbol"])

		quote_url = f'https://yfapi.net/v6/finance/quote?region=US&lang=en&symbols={"%2C".join(trending_list)}'
	
		response = requests.request("GET", quote_url, headers=headers)

		quote_container = response.json()["quoteResponse"]["result"]

		for quote in quote_container:
			symbol = quote["symbol"]
			currentPrice = round(quote["regularMarketPrice"],2)
			open_ = round(quote["regularMarketOpen"],2)
			volume = numerize.numerize(quote["regularMarketVolume"])
			trend_dict[symbol]= {"symbol":symbol, "currentPrice":currentPrice, "open":open_,
				"volume":volume}
		with open("static/json/trending_quote_backup.json", "w") as fp:
			json.dump(trend_dict, fp)

		return trend_dict
	except:
		# Handle API rate limits, in case of reaching maximum api calls or other potentiel errors
		with open("static/json/trending_quote_backup.json", "r") as fp:
			return json.load(fp)