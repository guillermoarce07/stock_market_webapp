from flask import Flask, request, render_template, jsonify
from app.utils.input_validator import validate_date
import pymysql
from app.dao.stock_price import StockPrice

app = Flask(__name__)
MARGIN_FOR_PREDICTION = 1000
NUMBER_OF_ENTRIES = 1000

# Configurations
app.config.from_object("config")

# Database connection
db = pymysql.connect(
    host=app.config["DB_HOST"],
    port=app.config["DB_PORT"],
    user=app.config["DB_USER"],
    passwd=app.config["DB_PASS"],
    db=app.config["DB_NAME"],
)

# HTTP error handling for 404
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.route("/getPrices")
def stock_api():

    # Get parameter from request
    datetime = request.args.get("datetime")

    # Validate input
    if not validate_date(datetime):
        return jsonify("invalid request")

    # Make query to database (it returns NUMBER_OF_ENTRIES entries from the specified date onwards.)
    cursor = db.cursor()
    query = (
        "SELECT * FROM (SELECT CAST(datetime AS char) as date_, open, high, low, close, volume FROM stock WHERE datetime<=%s ORDER BY datetime DESC LIMIT "
        + str(NUMBER_OF_ENTRIES)
        + ") as s ORDER BY date_ ASC;"
    )
    cursor.execute(query, (datetime,))
    prices = cursor.fetchall()

    # JSONIFY
    list_of_prices = []
    for p in prices:
        stock_price = StockPrice(p[0], p[1], p[2], p[3], p[4], p[5])
        list_of_prices.append(stock_price.__dict__)

    return jsonify(list_of_prices)


@app.route("/getRandomDate")
def random_date():

    # Make query to database
    cursor = db.cursor()
    query = (
        "SELECT CAST(datetime AS char) FROM (SELECT * FROM stock LIMIT "
        + str(MARGIN_FOR_PREDICTION)
        + ", 18446744073709551615) as marginForPrediction ORDER BY RAND() LIMIT 1;"
    )
    cursor.execute(query)
    date = cursor.fetchall()

    return jsonify(date)


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
