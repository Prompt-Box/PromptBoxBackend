
from flask import Flask, render_template, jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy
import numpy as np
from hmmlearn import hmm
#import model
app = Flask(__name__)

#sample JSON formatted Game, to be replaced with SQL database
# lobby format: id: int, title: str, players: list(str), num_players: int

def serialize_lobby(l):
    return {
        "title": l.title,
        "player1": l.player1,
        "num_players": l.num_players,
    }

def serialize_game(g):
    return {
        "title": g.title,
        "player1": g.player1,
        "player1_score": g.player1_score,
        "player2": g.player2,
        "player2_score": g.player2_score,
        "player1_turn": g.player1_turn,
        "round": g.round,
    }


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Lobby(db.Model):
    #id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    title = db.Column(db.String(120), primary_key=True, unique=True, nullable=False)
    player1 = db.Column(db.String(50), nullable=False)
    num_players = db.Column(db.Integer, nullable=False)

class Game(db.Model):
    #id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    title = db.Column(db.String(120), primary_key=True, unique=True, nullable=False)
    player1 = db.Column(db.String(50), nullable=False)
    player1_score = db.Column(db.Integer, nullable=False)
    player2 = db.Column(db.String(50), nullable=False)
    player2_score = db.Column(db.Integer, nullable=False)
    player1_turn = db.Column(db.Boolean, nullable=False)
    round = db.Column(db.Integer, nullable=False)

db.create_all()



#languageModel, dictionary = [], {}

# Placeholder Function to create AI-Generated Text
"""Test Functions"""
"""
def get_text(user_input):

    #Generate Text
    network = model.loadModel()
    symbols, states = network.sample(50)
    output = ""
    for num in np.squeeze(symbols):
        if(num >= 0 and num < len(languageModel)):
            output += languageModel[int(num)] + " "

    return output
"""
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

    lobbies = [serialize_lobby(lobby) for lobby in Lobby.query.all()]
    db.session.close()
    response = jsonify({"lobbies" : lobbies})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Let a Player Join a Lobby
@app.route('/api/lobby/join/<string:title>/<string:name>', methods=["POST"])
def join_game(title, name):
    lobby = Lobby.query.get(title)
    if not lobby:
        return Response(
            "Lobby Title Not valid",
            status=400,
        )
    new_game = Game(
        title = lobby.title,
        player1 = lobby.player1,
        player1_score = 0,
        player2 = name,
        player2_score = 0,
        player1_turn = True,
        round = 1,
    )
    # Delete Lobby as it is already being used, Add Game
    db.session.delete(lobby)
    db.session.add(new_game)
    db.session.commit()
    response = jsonify({"game" : serialize_game(new_game)})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Let a Player Create a Lobby
@app.route('/api/lobby/create/<string:title>/<string:name>', methods=["POST"])
def create_game(title, name):
    # If title already used
    if Lobby.query.get(title) or Game.query.get(title):
        response = jsonify("Title already used")
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    new_lobby = Lobby(title = title, player1 = name, num_players = 1)
    db.session.add(new_lobby)
    db.session.commit()
    response = jsonify(serialize_lobby(new_lobby))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

"""GAME FUNCTIONS"""
# Return Game status
@app.route('/api/games/<string:title>', methods=['GET'])
def get_game(title):
    game = Game.query.get(title)
    if not game:
        return Response(
            "Game ID Not valid",
            status=400,
        )

    response = jsonify({"game" : serialize_game(game)})
    response.headers.add('Access-Control-Allow-Origin', '*')
    db.session.close()
    return response



"""Methods to update a game"""

# Update Score
@app.route('/api/games/<string:title>/<string:name>', methods=['POST'])
def update_score(title, name):
    game = Game.query.get(title)
    if not game:
        return Response(
            "Game Title Not valid",
            status=400,
        )
    if game.player1 == name:
        game.player1_score += 1
    elif game.player2 == name:
        game.player2_score += 1
    else:
        return Response(
            "Game Name Not valid",
            status=400,
        )

    db.session.commit()
    response = jsonify("score updated")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Update Turn
@app.route('/api/games/<string:title>/turn', methods=['POST'])
def update_turn(title):
    game = Game.query.get(title)
    if not game:
        return Response(
            "Game Title Not valid",
            status=400,
        )

    game.player1_turn =  not game.player1_turn

    db.session.commit()
    response = jsonify("score updated")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Update Round
@app.route('/api/games/<string:title>/round', methods=['POST'])
def update_round(title):
    game = Game.query.get(title)
    if not game:
        return Response(
            "Game Title Not valid",
            status=400,
        )

    game.round += 1

    db.session.commit()
    db.session.close()
    response = jsonify("round updated")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/games/<string:title>/end', methods=['DELETE'])
def end_game(title):
    game = Game.query.get(title)
    db.session.delete(game)
    db.session.commit()
    response = jsonify("game deleted")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response





if __name__ == '__main__':

    #Create model and train, only temporary, will be timed later
    #languageModel, dictionary = model.buildLanguageModelFromText()
    #network = model.createModel()
    #network = model.trainModel(network, languageModel, dictionary)

    # threaded, so many users can use
    app.run(threaded=True)
