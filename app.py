
from flask import Flask, render_template
from transformers import pipeline
app = Flask(__name__)

generator = pipeline('text-generation', model='gpt2')

out = generator("Hello World", max_length=30, num_return_sequences=1)


@app.route("/")
def hello():
    return str(out)

if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port = 4000)
