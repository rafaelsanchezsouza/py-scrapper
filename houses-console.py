from flask import Flask, request , jsonify
import requests  
import json  
from parsel import Selector  
import datetime  
import time  
  
app = Flask(__name__)  
  
@app.route('/properties', methods=['POST'])  
def properties():  
    negocio = request.json.get('negocio', 'venda')
    tipo = request.json.get('tipo', 'casas')    
    max_requests = request.json.get('max_requests', None)    
    tipo = "apartamentos"  
  
    if tipo == "terrenos":  
        base_url = 'https://www.olx.com.br/imoveis/terrenos/estado-pb/paraiba/joao-pessoa'  
    else:  
        base_url = f'https://www.olx.com.br/imoveis/{negocio}/{tipo}/estado-pb/paraiba/joao-pessoa'  
    headers = {  
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'  
    }  
  
    all_properties = fetch_properties(base_url, headers, max_requests)  
    save_to_file(all_properties, negocio, tipo)  
  
    return jsonify(all_properties), 200  
  
  
def fetch_properties(base_url, headers, max_pages=None):  
    all_properties = []  
    num_consecutive_empty_pages = 0  
    page_number = 1  
  
    while num_consecutive_empty_pages < 5 and (max_pages is None or page_number <= max_pages):  
        print(f"Fetching page: {page_number}...")  
        url = base_url + '?o=' + str(page_number) if page_number != 1 else base_url  
        response = requests.get(url, headers=headers)  
  
        if response.status_code == 200:  
            selector = Selector(text=response.text)  
            html = selector.xpath('//script[@id="__NEXT_DATA__"]/text()').get()  
            data = json.loads(html)  
  
            properties = data.get('props', {}).get('pageProps', {}).get('ads', [])  
  
            if not properties:  
                num_consecutive_empty_pages += 1  
            else:  
                num_consecutive_empty_pages = 0  
  
            for property in properties:  
                property_data = {  
                    "subject": property.get('subject'),  
                    "title": property.get('title'),  
                    "price": property.get('price'),  
                    "listId": property.get('listId'),  
                    "lastBumpAgeSecs": property.get('lastBumpAgeSecs'),  
                    "oldPrice": property.get('oldPrice'),  
                    "professionalAd": property.get('professionalAd'),  
                    "isFeatured": property.get('isFeatured'),  
                    "listingCategoryId": property.get('listingCategoryId'),  
                    "images": [  
                        {  
                            "original": img.get('original'),  
                            "originalAlt": img.get('originalAlt'),  
                            "originalWebP": img.get('originalWebP'),  
                            "thumbnail": img.get('thumbnail')  
                        } for img in property.get('images', [])  
                    ],  
                    "url": property.get('url'),  
                    "thumbnail": property.get('thumbnail'),  
                    "date": property.get('date'),  
                    "imageCount": property.get('imageCount'),  
                    "location": property.get('location'),  
                    "locationDetails": property.get('locationDetails'),  
                    "category": property.get('category'),  
                    "searchCategoryLevelZero": property.get('searchCategoryLevelZero'),  
                    "searchCategoryLevelOne": property.get('searchCategoryLevelOne'),  
                    "properties": [  
                        {  
                            "name": prop.get('name'),  
                            "label": prop.get('label'),  
                            "value": prop.get('value')  
                        } for prop in property.get('properties', [])  
                    ]  
                }  
                all_properties.append(property_data)  
        else:  
            print(f"Request to {url} returned an error. Status code: {response.status_code}")  
  
        time.sleep(3)  # Add a 3-second delay  
        page_number += 1  
  
    print(f"Total properties fetched: {len(all_properties)}")  
    return all_properties  

  
  
def save_to_file(all_properties, negocio, tipo):  
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")  
    filename = "./buscas/" + timestamp + f"_{negocio}-{tipo}-{len(all_properties)}.json"  
  
    with open(filename, 'w', encoding='utf-8') as file:  
        json.dump(all_properties, file, ensure_ascii=False) 
  
  
if __name__ == "__main__":  
    app.run(debug=True, port=5555)  
