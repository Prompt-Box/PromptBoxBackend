
from flask import Flask, render_template, jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
import numpy as np
import uuid
import random
from hmmlearn import hmm
#import model
import markovify
import pickle
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
        "player1_text": g.player1_text,
        "player1_score": g.player1_score,
        "player2": g.player2,
        "player2_text": g.player2_text,
        "player2_score": g.player2_score,
        "player1_hasGone": g.player1_hasGone,
        "player2_hasGone": g.player2_hasGone,
        "round": g.round,
    }


NUMBER_OF_ROUNDS = 5

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

#Build markovify model
with open("hmm.pkl", "rb") as f:
    model = pickle.load(f)

model = markovify.Text.from_json(model)

class Lobby(db.Model):
    #id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    #id = db.Column(db.String, primary_key=False, default=uuid.uuid4, unique=True, nullable=False)
    title = db.Column(db.String(120), primary_key=True, unique=True, nullable=False)
    player1 = db.Column(db.String(50), nullable=False)
    num_players = db.Column(db.Integer, nullable=False)

class Game(db.Model):
    #id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    #id = db.Column(db.String, primary_key=False, default=uuid.uuid4, unique=True, nullable=False)
    title = db.Column(db.String(120), primary_key=True, unique=True, nullable=False)
    player1 = db.Column(db.String(50), nullable=False)
    player1_text = db.Column(db.String(200), nullable=False)
    player1_score = db.Column(db.Integer, nullable=False)
    player2 = db.Column(db.String(50), nullable=False)
    player2_text = db.Column(db.String(200), nullable=False)
    player2_score = db.Column(db.Integer, nullable=False)
    player1_turn = db.Column(db.Boolean, nullable=False)
    player1_hasGone = db.Column(db.Boolean, nullable=False)
    player2_hasGone = db.Column(db.Boolean, nullable=False)
    round = db.Column(db.Integer, nullable=False)

db.create_all()




# Placeholder Function to create AI-Generated Text
"""Test Functions"""

def generate_text():

    #languageModel, dictionary = model.loadLanguage()

    #Generate Text
    #network = model.loadModel()
    #symbols, states = network.sample(10)
    #output = ""
    #for num in np.squeeze(symbols):
    #    if(num >= 0 and num < len(languageModel)):
    #        output += languageModel[int(num)] + " "

    return model.make_sentence()

@app.route("/")
def hello():
    return "Hello World"




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
        player1_text = "",
        player1_score = 0,
        player2 = name,
        player2_text = "",
        player2_score = 0,
        player1_turn = True,
        player1_hasGone = False,
        player2_hasGone = False,
        round = 1,
    )
    # Delete Lobby as it is already being used, Add Game
    db.session.delete(lobby)
    db.session.add(new_game)
    db.session.commit()
    response = jsonify({"game" : serialize_game(new_game)})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Let a Player add their text
@app.route('/api/games/text/<string:title>/<string:name>', methods=["POST"])
def save_text(title, name):
    game = Game.query.get(title)
    generatedText = request.args.get('text')

    if(not game):
        return Response(
            "Game Title Not valid",
            status=400,
        )

    #Check whose turn it is
    if(game.player1 == name):
        #It's player 1's turn
        game.player1_text = generatedText
        db.session.commit()

        response = jsonify({"game" : serialize_game(game)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        db.session.close()
        return response
    else:
        #It's player 2's turn
        game.player2_text = generatedText
        db.session.commit()

        response = jsonify({"game" : serialize_game(game)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        db.session.close()
        return response

# Let a Player get texts to guess from
@app.route('/api/games/guess/<string:title>/<string:name>', methods=["GET"])
def get_text(title, name):
    game = Game.query.get(title)

    if(not game):
        return Response(
            "Game Title Not valid",
            status=400,
        )

    texts = []
    texts.append(generate_text())
    texts.append(generate_text())
    texts.append(generate_text())
    if(game.player1 == name):
            texts.append(game.player2_text)
    else:
            texts.append(game.player1_text)
    random.shuffle(texts)

    response = jsonify({"text" : texts})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# Let a Player check if their guess is right
@app.route('/api/games/check/<string:title>/<string:name>', methods=["GET"])
def get_answer(title, name):
    game = Game.query.get(title)
    if(not game):
        return Response(
            "Game Title Not valid",
            status=400,
        )

    textToCheck = request.args.get('text')
    response = None
    if(name == game.player1):
        if(textToCheck == game.player2_text):
            response = jsonify({"result" : 1})
        else:
            response = jsonify({"result" : 0})
    elif(name == game.player2):
        if(textToCheck == game.player1_text):
            response = jsonify({"result" : 1})
        else:
            response = jsonify({"result" : 0})

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

# Update hasGone
@app.route('/api/games/<string:title>/<string:name>/gone', methods=['POST'])
def update_hasGone(title, name):
    game = Game.query.get(title)
    if not game:
        return Response(
            "Game Title Not valid",
            status=400,
        )

    if name == game.player1:
        game.player1_hasGone = not game.player1_hasGone

    elif name == game.player2:
        game.player2_hasGone = not game.player2_hasGone

    else:
        return Response(
            "Player Name Not valid",
            status=400,
        )

    if game.player1_hasGone == True and game.player2_hasGone == True:
        game.round += 1

        #Set round to negative when game is over
        if(game.round > NUMBER_OF_ROUNDS):
            game.round = -1

        game.player1_text = ""
        game.player2_text = ""
        game.player1_turn = True

        game.player1_hasGone, game.player2_hasGone = False, False


    db.session.commit()
    response = jsonify("hasGone updated")
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

    #Set round to negative when game is over
    if(game.round > NUMBER_OF_ROUNDS):
        game.round = -1

    game.player1_text = ""
    game.player2_text = ""
    game.player1_turn = True

    db.session.commit()
    db.session.close()
    response = jsonify({"game" : serialize_game(game)})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

@app.route('/api/games/<string:title>/end', methods=['DELETE'])
def end_game(title):
    game = Game.query.get(title)
    if not game:
        return Response(
            "Game Title Not valid",
            status=400,
        )
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
