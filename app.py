from flask import Flask, render_template
import csv
app = Flask(__name__)
@app.get('/')
def index():
    movies = []
    with open('movies.csv', mode='r', encoding='UTF-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            movies.append(row)
    return render_template("index.html", movies=movies)


if __name__ == "__main__":
    app.run(debug=True)