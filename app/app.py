from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Restore HDMI'

@app.route('/submit')
def recommend():
  return 'hola'

if __name__ == '__main__':
    app.run(debug=True)

