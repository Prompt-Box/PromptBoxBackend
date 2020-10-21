
from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

#sample JSON formatted Game, to be replaced with SQL database
lobbies = [
    {
        'id': 1,
        'title': u'Prompt Box Party',
        'description': u'This game is not full, please join!',
        'num_players': 0,
    },

    {
        'id': 2,
        'title': u'Game is Full',
        'description': u'This game is already full. Sorry = (',
        'num_players': 2
    }
]

active_games = [
    {
        'id': 1,
        'players': [u'Max', u'Akhil'],
        'player1_turn': True,
        'score': [0, 0],
        'round': 1

    }
]

# Placeholder Function to create AI-Generated Text
def get_text(user_input):
    str = """Lorem ipsum dolor sit amet, consectetur adipiscing elit,
    sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim
    ad minim veniam, quis nostrud exercitation ullamco
    laboris nisi ut aliquip ex ea"""
    return user_input + " " + str

@app.route("/")
def hello():
    return "Hello World"

# Simple Route to Return Generated Text
@app.route('/api/generate_text/<string:input>', methods=["GET"])
def generate_text(input):
    return jsonify({'generated_text': get_text(input)})

# Return All Active Lobbies
@app.route('/api/games', methods=["GET"])
def get_games():
    return jsonify({'games': lobbies})

# Return All Open Lobbies
@app.route('/api/games/open', methods=['GET'])
def get_task():
    open_games = [game for game in lobbies if game['num_players'] < 2]
    return jsonify({'games': open_games})

@app.route('/api/games/active/<int: game_id>', methods=['GET'])
def get_games_by_id():
    game = [game for game in active_games if game['id']== game_id]
    return jsonify({'game': game})



if __name__ == '__main__':
    # threaded, so many users can use
    app.run(threaded=True, port=4000)
