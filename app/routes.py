from app import app
from flask import render_template, request, redirect, url_for
from bs4 import BeautifulSoup
import pandas as pd 
import numpy as np 
import requests
import json
import os
from app import utils
@app.route('/')
def index():
    return render_template("index.html")

# @app.route('/hello')
# @app.route('/hello/<name>')
# def hello(name= "World"):
#     return f"Hello, {name}!"

@app.route('/extract', methods=['POST','GET'])
def extract():
    if request.method == "POST":
        product_id = request.form.get("product_id")
        url = f"https://www.ceneo.pl/{product_id}"
        response = requests.get(url)
        if response.status_code == requests.codes['ok']:
            page_dom=BeautifulSoup(response.text, "html.parser")
           
            opinions_count = utils.extract(page_dom, "a.product-review__link > span")
            if opinions_count:
                url = f"https://www.ceneo.pl/{product_id}"
                all_opinions = []
                while(url):
                    print(url)
                    response = requests.get(url)
                    page_dom = BeautifulSoup(response.text, "html.parser")
                    opinions = page_dom.select("div.js_product-review")
                    for opinion in opinions:
                        single_opinion = {
                            key: utils.extract(opinion, *value)
                            for key, value in utils.selectors.items()
                        }
                        all_opinions.append(single_opinion)
                    try: 
                        url = "https://www.ceneo.pl"+utils.extract(page_dom,"a.pagination__next","href")
                    except TypeError:
                        url = None
                    if not os.path.exists("app/data"):
                        os.mkdir("app/data")

                    if not os.path.exists("app/data/opinions"):
                        os.mkdir("app/data/opinions")

                    with open(f"app/data/opinions/{product_id}.json","w",encoding="UTF-8") as jf:
                        json.dump(all_opinions, jf, indent = 4, ensure_ascii = False )
                    opinions = pd.DataFrame.from_dict(all_opinions)
                    pros_count = opinions.pros.apply(lambda p: True if p else False).sum()
                    cons_count = opinions.pros.apply(lambda p: True if p else False).sum()
                    opinions.recommendation = opinions.recommendation.apply(lambda r: "Brak rekomendacji")
                    stats = {

                    }

                if not os.path.exists("app/data/stats"):
                    os.mkdir("app/data/stats")

                with open(f"app/data/stats/{product_id}.json","w",encoding="UTF-8") as jf:
                    json.dump(stats, jf, indent = 4, ensure_ascii = False )

                return redirect(url_for('product',product_id = product_id))
            error = "Dany produkt nie posiada jeszcze żadnej opinii." 
            return render_template('extract.html', error = error)  
        error = "Produkt o danym id nie istnieje." 
        return render_template("extract.html", error = error)
    return render_template("extract.html")


@app.route('/author')
def author():
    return render_template("author.html")

@app.route('/products')
def products():
    products  = [filename.split(".")[0] for filename in os.listdir("app/data/opinions")]

    return render_template('products.html', products = products)

# @app.route('/author')
# def author():
#     return render_template("author.html")

@app.route('/product/<product_id>')
def product(product_id):
    return render_template('product.html', product_id = product_id)