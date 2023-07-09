import requests
import pickle
import csv
from flask import Flask, flash, redirect, render_template, request, url_for, abort, jsonify

response = requests.get("http://api.nbp.pl/api/exchangerates/tables/C?format=json")
data = response.json()

with open('filename.pickle', 'wb') as handle:
    pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('filename.pickle', 'rb') as handle:
    unserialized_data = pickle.load(handle)

rates = unserialized_data[0]["rates"]

with open("kantor.csv", "w", newline="") as file:
    writer = csv.writer(file, delimiter=";")
    writer.writerow(["currency", "code", "bid", "ask"]) 
    for rate in rates:
        writer.writerow([rate["currency"], rate["code"], rate["bid"], rate["ask"]])

app = Flask(__name__)

@app.route("/", methods=["GET"])
def currency_selector():
    return render_template("calculator.html", rates=rates)

currency_values = {}

with open("kantor.csv", "r", newline="") as file:
    reader = csv.reader(file, delimiter=";")
    next(reader)  # Skip the header row
    for row in reader:
        currency = row[1]
        bid = float(row[2])
        currency_values[currency] = bid

@app.route("/api/v1/calc/", methods=["POST"])
def calculator_itself():
    if not request.form:
        abort(400)

    currency = request.form.get("currency")
    number = float(request.form.get("number"))

    if currency in currency_values:
        currency_bid = currency_values[currency]
        result = number * currency_bid
        result = "{:.2f} PLN".format(result)
    else:
        return jsonify({"error": "Invalid currency"})
    return render_template("calculator.html", rates=rates, result=result)

if __name__ == '__main__':
    app.run(debug=True)
