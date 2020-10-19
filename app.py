
from flask import Flask, render_template
from transformers import pipeline
app = Flask(__name__)



@app.route("/")
def hello():
    return "Hello World"

@app.route('/text/<string:input>')
def generate_text(input):
    generator = pipeline('text-generation', model='gpt2')
    out = generator(input, max_length=30, num_return_sequences=1)

    return str(out)


if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port = 4000)
