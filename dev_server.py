from flask import Flask, render_template, request, jsonify

# define the app
app = Flask(__name__)

# define the logger
logger = CustomLogger('dev_server')
logger.setLevel('DEBUG')

@app.route("/")
def index():
  html_content = render_template("index.html", color=color)
  return html_content

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5001, debug=False)