import requests
import json

class QuoteManager:
    def __init__(self):
        self.api_url = "https://zenquotes.io/api/random"

    def get_quote(self):
        try:
            response = requests.get(self.api_url)
            if response.status_code == 200:
                data = response.json()
                quote = data[0].get('q', '')
                author = data[0].get('a', '')
                return f'"{quote}" -{author}'
            return "Success is not final, failure is not fatal. -Winston Churchill"
        except:
            return "The only way to do great work is to love what you do. -Steve Jobs" 