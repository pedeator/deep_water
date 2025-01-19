import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from flask import Flask, render_template_string, request, send_file
import io

app = Flask(__name__)

# ---------------------------------------------------------------------------------------
# 1) A large dictionary: brand -> list of (model_name, model_url) pairs.
#    Incorporated all the links you provided, grouped by brand.
# ---------------------------------------------------------------------------------------
BRAND_MODEL_MAP = {
    "Ford": [
        ("Focus 2011-2015", "https://otoparts.ge/product-category/ford/focus-2011-2015/"),
        ("Focus 2012-2015", "https://otoparts.ge/product-category/ford/focus-2012-2015/"),
        ("Focus 15-16", "https://otoparts.ge/product-category/ford/focus-15-16/"),
        ("Mustang 2010-2012", "https://otoparts.ge/product-category/ford/mustang-2010-2012/"),
        ("Mustang 2015-2017", "https://otoparts.ge/product-category/ford/mustang-2015-2017/"),
        ("Fusion 13-16", "https://otoparts.ge/product-category/ford/fusion-13-16/"),
        ("Fusion 16-18", "https://otoparts.ge/product-category/ford/fusion-16-18/"),
        ("Fusion 2019-on", "https://otoparts.ge/product-category/ford/fusion-2019-on/"),
        ("Fiesta 11-17", "https://otoparts.ge/product-category/ford/fiesta-11-17/"),
        ("Ecosport 2018-2023", "https://otoparts.ge/product-category/ford/ecosport-2018-2023/"),
        ("Escape 2017-2019", "https://otoparts.ge/product-category/ford/escape-2017-2019/"),
        ("Escape 2020-2023", "https://otoparts.ge/product-category/ford/escape-2020-2023/"),
        ("Explorer 2016-2019", "https://otoparts.ge/product-category/ford/explorer-2016-2019/"),
        ("Explorer 2020-on", "https://otoparts.ge/product-category/ford/explorer-2020-on/")
    ],
    "Audi": [
        ("A4 2007-2011", "https://otoparts.ge/product-category/audi/a4-2007-2011/"),
        ("A4 2013-2015", "https://otoparts.ge/product-category/audi/a4-2013-2015/"),
        ("A4 2016-2018", "https://otoparts.ge/product-category/audi/a4-2016-2018/"),
        ("A4 2020-on", "https://otoparts.ge/product-category/audi/a4-2020-on/"),
        ("A5 2013-2017", "https://otoparts.ge/product-category/audi/a5-2013-2017/"),
        ("A5 2017-2019", "https://otoparts.ge/product-category/audi/a5-2017-2019/"),
        ("A6 2008-2010", "https://otoparts.ge/product-category/audi/a6-2008-2010/"),
        ("A6 2013-2015", "https://otoparts.ge/product-category/audi/a6-2013-2015/"),
        ("A6 2016-2018", "https://otoparts.ge/product-category/audi/a6-2016-2018/"),
        ("A7 2011-2015", "https://otoparts.ge/product-category/audi/a7-2011-2015/"),
        ("A7 2016-2018", "https://otoparts.ge/product-category/audi/a7-2016-2018/"),
        ("Q3 2014-2018", "https://otoparts.ge/product-category/audi/q3-2014-2018/"),
        ("Q5 2008-2012", "https://otoparts.ge/product-category/audi/q5-2008-2012/"),
        ("Q5 2013-on", "https://otoparts.ge/product-category/audi/q5-2013-on/"),
        ("Q5 2017-2020", "https://otoparts.ge/product-category/audi/q5-2017-2020/"),
        ("Q7 2009-2015", "https://otoparts.ge/product-category/audi/q7-2009-2015/"),
        ("Q7 2016-2019", "https://otoparts.ge/product-category/audi/q7-2016-2019/")
    ],
    "BMW": [
        ("3-series f30 2015-2018", "https://otoparts.ge/product-category/bmw/3-series-f30-2015-2018/"),
        ("3-series e46 2002-2005", "https://otoparts.ge/product-category/bmw/3-series-e46-2002-2005/"),
        ("3-series 2008-2013", "https://otoparts.ge/product-category/bmw/3-series-2008-2013/"),
        ("3-series f30 2012-2015", "https://otoparts.ge/product-category/bmw/3-series-f30-2012-2015/"),
        ("3-series g20 2019-2021", "https://otoparts.ge/product-category/bmw/3-series-g-20-2019-2021/"),
        ("4-series f32 2014-2017", "https://otoparts.ge/product-category/bmw/4-series-f32-2014-2017/"),
        ("5-series f10 2010-2013", "https://otoparts.ge/product-category/bmw/5-series-f10-2010-2013/"),
        ("5-series f10 2014-2017", "https://otoparts.ge/product-category/bmw/5-series-f10-2014-2017/"),
        ("5-series 2017-on", "https://otoparts.ge/product-category/bmw/5-series-2017-on/"),
        ("x5 e70 2007-2010", "https://otoparts.ge/product-category/bmw/x5-e70-2007-2010/"),
        ("x5 e70 2011-2013", "https://otoparts.ge/product-category/bmw/x5-e70-2011-2013/"),
        ("x5 f15 2014-2018", "https://otoparts.ge/product-category/bmw/x5-f15-2014-2018/"),
        ("x5 g05 2019-2023", "https://otoparts.ge/product-category/bmw/x5-g05-2019-2023/"),
        ("x6 e71 2007-2013", "https://otoparts.ge/product-category/bmw/x6-e71-2007-2013/")
    ],
    "Chevrolet": [
        ("Camaro 2008-2013", "https://otoparts.ge/product-category/chevrolet/camaro-2008-2013/"),
        ("Camaro 2014-2015", "https://otoparts.ge/product-category/chevrolet/camaro-2014-2015/"),
        ("Cruze 2011-2015", "https://otoparts.ge/product-category/chevrolet/cruze-2011-2015/"),
        ("Cruze 2016-2019", "https://otoparts.ge/product-category/chevrolet/cruze-2016-2019/"),
        ("Cruze 2019", "https://otoparts.ge/product-category/chevrolet/cruze-2019/"),
        ("Malibu 2013-2015", "https://otoparts.ge/product-category/chevrolet/malibu-2013-2015/"),
        ("Malibu 2015-on", "https://otoparts.ge/product-category/chevrolet/malibu-2015-on/"),
        ("Malibu 2019", "https://otoparts.ge/product-category/chevrolet/malibu-2019/"),
        ("Trax 2017-2021", "https://otoparts.ge/product-category/chevrolet/trax-2017-2021/"),
        ("Equinox 2017-2021", "https://otoparts.ge/product-category/chevrolet/equinox-2017-2021/")
    ],
    "Fiat": [
        ("500 2007-2014", "https://otoparts.ge/product-category/fiat/500-2007-2014/")
    ],
    "Honda": [
        ("Accord 2018-2020", "https://otoparts.ge/product-category/honda/accord-2018-2020/"),
        ("Accord 2020-2022", "https://otoparts.ge/product-category/honda/accord-2020-2022/"),
        ("Civic 2011-2013", "https://otoparts.ge/product-category/honda/civic-2011-2013/"),
        ("Civic 2012-2015", "https://otoparts.ge/product-category/honda/civic-2012-2015/"),
        ("Civic 2016-on", "https://otoparts.ge/product-category/honda/civic-2016-on/"),
        ("CR-V 2012-2015", "https://otoparts.ge/product-category/honda/cr-v-2012-2015/"),
        ("CR-V 2017-2019", "https://otoparts.ge/product-category/honda/cr-v-2017-2019/"),
        ("CR-V 2020-2024", "https://otoparts.ge/product-category/honda/cr-v-2020-2024/"),
        ("HR-V 2016-2020", "https://otoparts.ge/product-category/honda/hr-v-2016-2020/"),
        ("Insight 2011-2015", "https://otoparts.ge/product-category/honda/insight-2011-2015/"),
        ("Fit 2008-2014", "https://otoparts.ge/product-category/honda/fit-2008-2014/"),
        ("Fit 2014-on", "https://otoparts.ge/product-category/honda/fit-2014-on/")
    ],
    "Hyundai": [
        ("Accent 2011-2015", "https://otoparts.ge/product-category/hyundai/accent-2011-2015/"),
        ("Accent 2016-on", "https://otoparts.ge/product-category/hyundai/accent-2016-on/"),
        ("Elantra 2011-2013", "https://otoparts.ge/product-category/hyundai/elantra-2011-2013/"),
        ("Elantra 2014-2015", "https://otoparts.ge/product-category/hyundai/elantra-2014-2015/"),
        ("Elantra 2015-on", "https://otoparts.ge/product-category/hyundai/elantra-2015-on/"),
        ("Elantra 2019", "https://otoparts.ge/product-category/hyundai/elantra-2019/"),
        ("Elantra 2021-2022", "https://otoparts.ge/product-category/hyundai/elantra-2021-2022/"),
        ("Elantra GT 2011-2017", "https://otoparts.ge/product-category/hyundai/elantra-gt-2011-2017/"),
        ("ix35 2010-2015", "https://otoparts.ge/product-category/hyundai/ix-35-2010-2015/"),
        ("ix35 2015-on", "https://otoparts.ge/product-category/hyundai/ix-35-2015-on/"),
        ("Tucson 2019-2021", "https://otoparts.ge/product-category/hyundai/tucson-2019-2021/"),
        ("Tucson 2022-on", "https://otoparts.ge/product-category/hyundai/tucson-2022-on/"),
        ("Santa Fe 2012-2015", "https://otoparts.ge/product-category/hyundai/santa-fe-2012-2015/"),
        ("Santa Fe 2016-2018", "https://otoparts.ge/product-category/hyundai/santa-fe-2016-2018/"),
        ("Santa Fe 2019-2021", "https://otoparts.ge/product-category/hyundai/santa-fe-2019-2021/"),
        ("Sonata 2010-2012", "https://otoparts.ge/product-category/hyundai/sonata-2010-2012/"),
        ("Sonata 2013-2014 facelift", "https://otoparts.ge/product-category/hyundai/sonata-2013-2014-facelift/"),
        ("Sonata 2014-on", "https://otoparts.ge/product-category/hyundai/sonata-2014-on/"),
        ("Sonata 2018-2019", "https://otoparts.ge/product-category/hyundai/sonata-2018-2019/"),
        ("Sonata 2020-2022", "https://otoparts.ge/product-category/hyundai/sonata-2020-2022/"),
        ("Veloster 2011-on", "https://otoparts.ge/product-category/hyundai/veloster-2011-on/"),
        ("Kona 2018-2021", "https://otoparts.ge/product-category/hyundai/kona-2018-2021/"),
        ("Palisade 2020-on", "https://otoparts.ge/product-category/hyundai/palisade-2020-on/")
    ],
    "Kia": [
        ("Optima 2010-2013", "https://otoparts.ge/product-category/kia/optima-2010-2013/"),
        ("Optima 2013-2016", "https://otoparts.ge/product-category/kia/optima-2013-2016/"),
        ("Optima 2016-on", "https://otoparts.ge/product-category/kia/optima-2016-on/"),
        ("Optima 2018-2019", "https://otoparts.ge/product-category/kia/optima-2018-2019/"),
        ("Optima K5 2020-2023", "https://otoparts.ge/product-category/kia/optima-k5-2020-2023/"),
        ("Picanto 2011-2015", "https://otoparts.ge/product-category/kia/picanto-2011-2015/"),
        ("Picanto 2015-on", "https://otoparts.ge/product-category/kia/picanto-2015-on/"),
        ("Sportage 2010-2014", "https://otoparts.ge/product-category/kia/sportage-2010-2014/"),
        ("Sportage 2016-2019", "https://otoparts.ge/product-category/kia/sportage-2016-2019/"),
        ("Soul 2008-2014", "https://otoparts.ge/product-category/kia/soul-2008-2014/")
    ],
    "Lexus": [
        ("CT 200h 2012-2014", "https://otoparts.ge/product-category/lexus/ct-200h-2012-2014/"),
        ("CT 200h F Sport 2015-on", "https://otoparts.ge/product-category/lexus/ct-200h-f-sport-2015-on/"),
        ("CT 200h 2018", "https://otoparts.ge/product-category/lexus/ct-200h-2018/"),
        ("ES 2012-2015", "https://otoparts.ge/product-category/lexus/es-2012-2015/"),
        ("ES 2015-2018", "https://otoparts.ge/product-category/lexus/es-2015-2018/"),
        ("ES 2018-2020", "https://otoparts.ge/product-category/lexus/es-2018-2020/"),
        ("IS 250 2014-2016", "https://otoparts.ge/product-category/lexus/is-250-2014-2016/"),
        ("IS 2017-2018", "https://otoparts.ge/product-category/lexus/is-2017-2018/"),
        ("RX 2012-2015", "https://otoparts.ge/product-category/lexus/rx-2012-2015/"),
        ("RX 2016-on", "https://otoparts.ge/product-category/lexus/rx-2016-on/"),
        ("RX 2019-2021", "https://otoparts.ge/product-category/lexus/rx-2019-2021/"),
        ("NX 200 2014-on", "https://otoparts.ge/product-category/lexus/nx-200-2014-on/"),
        ("NX 2017-2020", "https://otoparts.ge/product-category/lexus/nx-2017-2020/"),
        ("HS 2012-on", "https://otoparts.ge/product-category/lexus/hs-2012-on/")
    ],
    "Mazda": [
        ("Mazda 3 2014-2016", "https://otoparts.ge/product-category/mazda/mazda-3-2014-2016/"),
        ("Mazda 3 2017-2018", "https://otoparts.ge/product-category/mazda/mazda-3-2017-2018/"),
        ("Mazda 3 2019-2022", "https://otoparts.ge/product-category/mazda/mazda-3-2019-2022/"),
        ("Mazda 6 2014-2016", "https://otoparts.ge/product-category/mazda/mazda-6-14-16/"),
        ("Mazda 6 2017-2019", "https://otoparts.ge/product-category/mazda/mazda-6-2017-2019/"),
        ("Mazda 6 2020-2022", "https://otoparts.ge/product-category/mazda/mazda-6-2020-2022/"),
        ("CX-5 2014-2016", "https://otoparts.ge/product-category/mazda/cx-5-2014-2016/"),
        ("CX-5 2017-2022", "https://otoparts.ge/product-category/mazda/mazda-cx5-2017-2022/"),
        ("CX-5 2022-on", "https://otoparts.ge/product-category/mazda/mazda-cx5-2022-on/")
    ],
    "Mercedes-Benz": [
        ("C-Class W204 2007-2010", "https://otoparts.ge/product-category/mercedes-benz/c-class-w204-2007-2010/"),
        ("C-Class W204 2011-2015", "https://otoparts.ge/product-category/mercedes-benz/c-class-w204-2011-2015/"),
        ("C-Class W205 2014-on", "https://otoparts.ge/product-category/mercedes-benz/c-class-w205-2014-on/"),
        ("CLA C117 2013-2016", "https://otoparts.ge/product-category/mercedes-benz/cla-c117-2013-2016/"),
        ("CLA C117 2016-2019", "https://otoparts.ge/product-category/mercedes-benz/cla-c117-2016-2019/"),
        ("CLS W218 2013-2016", "https://otoparts.ge/product-category/mercedes-benz/cls-w218-2013-2016/"),
        ("E-Class W212 2009-2013", "https://otoparts.ge/product-category/mercedes-benz/e-class-w212-2009-2013/"),
        ("E-Class W212 2013-2016", "https://otoparts.ge/product-category/mercedes-benz/e-class-w212-2013-2016/"),
        ("E 2017-2019", "https://otoparts.ge/product-category/mercedes-benz/e-2017-2019/"),
        ("S 221 2007-2013", "https://otoparts.ge/product-category/mercedes-benz/s-221-2007-2013/"),
        ("S 2018-2020", "https://otoparts.ge/product-category/mercedes-benz/s-2018-2020/"),
        ("GLK 2010-2015", "https://otoparts.ge/product-category/mercedes-benz/glk-2010-2015/"),
        ("GLA 2014-2016", "https://otoparts.ge/product-category/mercedes-benz/gla-2014-2016/"),
        ("GLA 2017-2019", "https://otoparts.ge/product-category/mercedes-benz/gla-2017-2019/"),
        ("ML 2008-2011", "https://otoparts.ge/product-category/mercedes-benz/ml-2008-2011/"),
        ("ML W166 2011-2015", "https://otoparts.ge/product-category/mercedes-benz/ml-w166-2011-2015/"),
        ("GL-Class X164 2009-2012", "https://otoparts.ge/product-category/mercedes-benz/gl-class-x164-2009-2012/"),
        ("X166 2013-2019", "https://otoparts.ge/product-category/mercedes-benz/x166-2013-2019/"),
        ("GLE W166 2015-on", "https://otoparts.ge/product-category/mercedes-benz/gle-w166-2015-on/"),
        ("GLE / GLE Coupe 2015-2019", "https://otoparts.ge/product-category/mercedes-benz/gle-gle-coupe-2015-2019/"),
        ("GLC 2015-2017", "https://otoparts.ge/product-category/mercedes-benz/glc-2015-2017/"),
        ("GLC 2018-2020", "https://otoparts.ge/product-category/mercedes-benz/glc-2018-2020/"),
        ("GLS X167 2020-on", "https://otoparts.ge/product-category/mercedes-benz/gls-x167-2020-on/"),
        ("GLE W167 2020-on", "https://otoparts.ge/product-category/mercedes-benz/gle-w167-2020-on/")
    ],
}

# ---------------------------------------------------------------------------------------
# 2) HTML templates for the pages. We use render_template_string for this MVP.
#    NOTE: We do not use "len(data)" in Jinja to avoid UndefinedError in some environments.
# ---------------------------------------------------------------------------------------

home_template = """
<!DOCTYPE html>
<html>
  <head>
    <title>Car Parts Scraper MVP</title>
  </head>
  <body>
    <h1>Car Parts Scraper MVP</h1>
    <p>Select the brand(s) and model(s) you want to scrape:</p>
    <form action="/scrape" method="POST">
      {% for brand, model_list in brand_map.items() %}
        <h2>{{ brand }}</h2>
        <ul style="list-style-type:none;">
           {% for model_name, link in model_list %}
             <li>
               <input type="checkbox" name="selected_links" value="{{ link }}" id="{{ brand }}-{{ model_name|replace(' ','_') }}">
               <label for="{{ brand }}-{{ model_name|replace(' ','_') }}">{{ model_name }}</label>
             </li>
           {% endfor %}
        </ul>
      {% endfor %}
      <br>
      <button type="submit">Scrape Selected Models</button>
    </form>
  </body>
</html>
"""

results_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Scraping Results</title>
</head>
<body>
    <h1>Scraping Complete</h1>
    <p>Total products found: <b>{{ data_len }}</b></p>

    <table border="1" cellpadding="5" cellspacing="0">
      <tr>
        <th>Product Name</th>
        <th>Price</th>
        <th>Category</th>
        <th>Availability</th>
      </tr>
      {% for row in data_list %}
      <tr>
        <td>{{ row['product_name'] }}</td>
        <td>{{ row['price'] }}</td>
        <td>{{ row['category'] }}</td>
        <td>{{ row['availability'] }}</td>
      </tr>
      {% endfor %}
    </table>

    <br>
    <a href="/download"><button>Download CSV</button></a>
    <a href="/"><button>Back</button></a>
</body>
</html>
"""

# ---------------------------------------------------------------------------------------
# 3) We store the final scraping results in a global DataFrame
# ---------------------------------------------------------------------------------------
scraped_df = pd.DataFrame()

# ---------------------------------------------------------------------------------------
# 4) Flask routes
# ---------------------------------------------------------------------------------------

@app.route("/")
def home():
    # Render the main page with all brand->models checkboxes
    return render_template_string(home_template, brand_map=BRAND_MODEL_MAP)

@app.route("/scrape", methods=["POST"])
def scrape():
    global scraped_df

    # 1. Collect all selected checkboxes
    selected_links = request.form.getlist("selected_links")

    # 2. We'll gather all row-dicts here
    all_rows = []

    # 3. For each selected link, do a GET request and parse
    for url in selected_links:
        time.sleep(1)  # optional delay
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                products = soup.select("ul.products li.product")

                for p in products:
                    name_el = p.select_one("h2.woocommerce-loop-product__title")
                    price_el = p.select_one("span.price")
                    category_el = p.select_one("span.premium-woo-product-category")

                    # Check for out-of-stock
                    is_out_of_stock = 'outofstock' in p.get("class", [])
                    availability = "Out of stock" if is_out_of_stock else "In stock"

                    product_name = name_el.get_text(strip=True) if name_el else "N/A"
                    price = price_el.get_text(strip=True) if price_el else "N/A"
                    category = category_el.get_text(strip=True) if category_el else "N/A"

                    all_rows.append({
                        "product_name": product_name,
                        "price": price,
                        "category": category,
                        "availability": availability
                    })
            else:
                print(f"Warning: {url} returned status {resp.status_code}")

        except Exception as e:
            print(f"Error scraping {url} => {e}")

    # 4. Put all data into a DataFrame
    if all_rows:
        scraped_df = pd.DataFrame(all_rows)
    else:
        scraped_df = pd.DataFrame(columns=["product_name","price","category","availability"])

    # 5. Convert to list of dicts for Jinja
    data_list = scraped_df.to_dict(orient="records")
    data_len = len(data_list)

    # 6. Render results page
    return render_template_string(
        results_template,
        data_list=data_list,
        data_len=data_len
    )

@app.route("/download")
def download():
    global scraped_df
    # Convert the final DF to CSV in memory
    output = io.StringIO()
    scraped_df.to_csv(output, index=False)
    csv_str = output.getvalue().encode("utf-8")
    output.close()

    # Return as a file download
    return send_file(
        io.BytesIO(csv_str),
        mimetype="text/csv",
        as_attachment=True,
        download_name="scraped_data.csv"
    )

if __name__ == "__main__":
    # If port 5000 is busy, choose a new port or free it up
    app.run(debug=True, host="0.0.0.0", port=5001)
