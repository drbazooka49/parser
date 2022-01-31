import time
import pstats
import cProfile
import WebSites
from flask import Flask, render_template, request

app = Flask(__name__)
unoClass = WebSites.Uno()
enterClass = WebSites.Enter()
darwinClass = WebSites.Darwin()

@app.route("/")
def home():
    return render_template('homepage.html')

@app.route("/uno/", methods=["POST", "GET"])
def uno():
    if request.method == "POST":
        search = request.form['search']
        items = unoClass.to_run(search)
        print(search)
        if not items:
            back_to = '/uno/'
            return render_template('noproducts.html', back_to=back_to)
        else:
            return render_template('search_results.html', imgs_dict=items)
    else:
        site = 'Uno'
        return render_template('search.html', site=site)

@app.route("/enter/", methods=["POST", "GET"])
def enter():
    if request.method == "POST":
        search = request.form['search']
        items = enterClass.to_run(search)
        if not items:
            back_to = '/enter/'
            return render_template('noproducts.html', back_to=back_to)
        else:
            return render_template('search_results.html', imgs_dict=items)
    else:
        site = 'Enter'
        return render_template('search.html', site=site)

@app.route("/darwin/", methods=["POST", "GET"])
def darwin():
    if request.method == "POST":
        search = request.form['search']
        items = darwinClass.to_run(search)
        if not items:
            back_to = '/darwin/'
            return render_template('noproducts.html', back_to=back_to)
        else:
            return render_template('search_results.html', imgs_dict=items)
    else:
        site = 'Darwin'
        return render_template('search.html', site=site)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8080)
