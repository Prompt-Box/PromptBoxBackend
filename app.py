
from flask import Flask, render_template, jsonify, request, Response
import numpy as np
from hmmlearn import hmm
import model
app = Flask(__name__)

#sample JSON formatted Game, to be replaced with SQL database
# lobby format: id: int, title: str, players: list(str), num_players: int

lobby = [
    {
        'id': 1,
        'title': u'Prompt Box Party',
        'players': [u'Max'],
        'num_players': 1,
    },

    {
        'id': 2,
        'title': u'Game is Full',
        'players': [u'Shay', u'Benny'],
        'num_players': 2
    }
]

# game format, id: int, title: str, players: list(str), player1_turn: True, score: list(int)
# round: 1
games = [
    {
        'id': 1,
        'players': {'Max': 0, 'Akhil': 0},
        'player1_turn': True,
        'round': 1

    }
]


languageModel, dictionary = [], {}

# Placeholder Function to create AI-Generated Text
"""Test Functions"""

def get_text(user_input):
    
    #Generate Text
    network = model.loadModel()
    symbols, states = network.sample(50)
    output = ""
    for num in np.squeeze(symbols):
        if(num >= 0 and num < len(languageModel)):
            output += languageModel[int(num)] + " "

    return output

@app.route("/")
def hello():
    return "Hello World"

# Simple Route to Return Generated Text
@app.route('/api/generate_text/<string:input>', methods=["GET"])
def generate_text(input):
    response = jsonify({'generated_text': get_text(input)})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

"""@app.route('/api/games/open', methods=['GET'])
def get_task():
    open_games = [game for game in lobbies if game['num_players'] < 2]
    return jsonify({'games': open_games})

@app.route('/api/games/active/<int: game_id>', methods=['GET'])
def get_games_by_id():
    game = [game for game in active_games if game['id']== game_id]
    return jsonify({'game': game})"""

"""Test Functions"""

# Return All Games that have not started
@app.route('/api/lobby', methods=["GET"])
def get_lobby():
    response = jsonify({'lobby': lobby})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Let a Player Join a Lobby
@app.route('/api/lobby/join/<int:id>/<string:name>', methods=["POST"])
def join_game(id, name):
    for l in lobby:
        if l['id'] == id:
            l['players'].append(name)
            l['num_players'] += 1
            # If the lobby is full, create a new game
            if l['num_players'] == 2:
                games.append({
                        'id': len(games) + 1,
                        'players': dict.fromkeys(l['players'], 0),
                        'player1_turn': True,
                        'round': 1
                })
                #
                return jsonify({'game':games[len(games)-1]}), 200

    # Passed Invalid Lobby ID
    return Response(
        "Lobby ID Not valid",
        status=400,
    )

# Let a Player Create a Lobby
@app.route('/api/lobby/create/<string:title>/<string:name>', methods=["POST"])
def create_game(title, name):
    lobby.append({
        'id': len(lobby)+1,
        'title': title,
        'players': [name],
        'num_players': 1
    })
    response = jsonify("True")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


# Return Game status
@app.route('/api/games/<int:id>', methods=['POST'])
def get_game(id):
    for game in games:
        if game['id'] == id:
            return jsonify({'games': game})

    return Response(
        "Game ID Not valid",
        status=400,
    )

"""Methods to update a game"""

# Update Score
@app.route('/api/games/<int:id>/<string:name>', methods=['POST'])
def update_score(id, name):
    for game in games:
        if game["id"] == id:
            game["players"][name] += 1
            return "Score Edited"
    return Response(
        "Game ID Not valid",
        status=400,
    )

# Update Turn
@app.route('/api/games/<int:id>/turn', methods=['POST'])
def update_turn(id):
    for game in games:
        if game["id"] == id:
            game["player1_turn"] = not game["player1_turn"]
            return "Turn Updated"
    return Response(
        "Game ID Not valid",
        status=400,
    )

# Update Round
@app.route('/api/games/<int:id>/round', methods=['POST'])
def update_round(id):
    for game in games:
        if game["id"] == id:
            game["round"] += 1
            return "Round Updated"
    return Response(
        "Game ID Not valid",
        status=400,
    )






if __name__ == '__main__':

    #Create model and train, only temporary, will be timed later
    languageModel, dictionary = model.buildLanguageModelFromText()
    network = model.createModel()
    #network = model.trainModel(network, languageModel, dictionary)
    
    # threaded, so many users can use
    app.run(threaded=True, port=4000)

