from flask import Flask, jsonify

app = Flask(__name__)

# Example API
@app.route('/api/hotels')
def get_hotels():
    data = [
        {'id': 1, 'name': 'Hotel Taj'},
        {'id': 2, 'name': 'Hotel Oberoi'}
    ]
    return jsonify(data)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
