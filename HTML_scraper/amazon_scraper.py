from datetime import datetime
import requests
import csv
import bs4
import concurrent.futures
from tqdm import tqdm


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
REQUEST_HEADER = {
    'User-Agent':USER_AGENT,
    'Accept-Language': 'en-US, en;q=0.5',   
}
NO_THREADS = 10

def get_page_html(url):
    res = requests.get(url, headers = REQUEST_HEADER)
    return res.content

def get_product_price(soup):
    main_price_span = soup.find('span', class_='a-offscreen')    
    if main_price_span:
        price = main_price_span.text.strip().replace('$', '').replace(',', '')
        try:
            return float(price)
        except ValueError:
            print("Value Obtained For Price Could Not Be Parsed")
            exit()
            
def get_product_title(soup):
    product_title = soup.find('span', id='productTitle')
    if product_title:
        return product_title.text.strip()
    else:
        return "Title Not Found"

def get_product_rating(soup):
    product_ratings_div = soup.find('div', attrs={
        'id': 'averageCustomerReviews'
    })
    product_rating_section = product_ratings_div.find(
        'i', attrs={'class': 'a-icon-star'})
    product_rating_span = product_rating_section.find('span')
    
    try:
        rating = product_rating_span.text.strip().split()
        return float(rating[0])
    except ValueError:
        print("Value Obtained For Rating Could Not Be Parsed")
        exit()
        
        
def get_product_technical_details(soup):
    details = {}
    technical_details_section = soup.find('div', id='prodDetails')
    data_tables = technical_details_section.find_all(
        'table', class_='prodDetTable')
    for table in data_tables:
        table_rows = table.find_all('tr')
        for row in table_rows:
            row_key = row.find('th').text.strip()
            row_value = row.find('td').text.strip().replace('\u200e', '')
            details[row_key] = row_value
    return details
        
def extract_product_info(url, output):
    product_info = {}
    html = get_page_html(url)
    soup = bs4.BeautifulSoup(html, 'lxml')
    product_info['price'] = get_product_price(soup)
    product_info['title'] = get_product_title(soup)
    product_info['rating'] = get_product_rating(soup)
    product_info.update(get_product_technical_details(soup))
    output.append(product_info) 
    
if __name__ == '__main__':
    
    products_data = []
    urls = []
    
    with open('amazon_products.csv','r', newline='') as csvfile:
        urls = list(csv.reader(csvfile, delimiter=','))
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=NO_THREADS) as executor:
        for wkn in tqdm(range(0, len(urls))):
            executor.submit(extract_product_info, urls[wkn][0], products_data)            
                   
    output_file_name = 'output-{}.csv'.format(
        datetime.today().strftime("%m-%d-%Y"))
    
    with open(output_file_name, 'w') as outputfile:
        writer = csv.writer(outputfile)
        writer.writerow(products_data[0].keys())
        for product in products_data:
            writer.writerow(product.values())