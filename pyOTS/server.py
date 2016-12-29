#!/usr/bin/python

from flask import Flask
from flask import jsonify
from flask import request
from ots import OTS

app = Flask(__name__)

@app.route('/view/<token>', methods=['GET'])
def view_secret(token):
    """Endpoint to return data about the secret"""
    response = ots.view_secret(token)
    return response


@app.route('/open', methods=['POST'])
def open_secret():
    """Endpoint to open the secret"""
    post_content = request.get_json(silent=False)
    required_fields = {'token', 'password'}     
    if post_content is None:
        return '{ "Error" : "json data required" }', 400
    elif not required_fields <= set(post_content):
        return '{ "Error": "There are missing fields in the request" }', 400
    elif post_content['token'] == "":
        return '{ "Error": "Message field cannot be empty" }', 400
    else:
        response = ots.open_secret(post_content['token'], post_content['password'])
    return response


@app.route('/create', methods=['POST'])
def create_secret():
    """Endpoint to create the secret"""
    post_content = request.get_json(silent=False)
    required_fields = {'message'}
    if post_content is None:
        return '{ "Error" : "json data required" }', 400
    elif not required_fields <= set(post_content):
        return '{ "Error": "There are missing fields in the request" }', 400
    elif post_content['message'] == "":
        return '{ "Error": "Message field cannot be empty" }', 400
    else:
        response = ots.create_secret(post_content['message'], post_content['password'],
                                     post_content['ttl'])
    return response

@app.route('/delete/<token>', methods=['DELETE'])
def delete_secret(token):
    """Endpoint to delete a secret"""
    response = ots.delete_secret(token)
    return response


@app.route('/random-password', methods=['GET'])
def random_password():
    """Endpoint that returns a random password"""
    response = ots.generate_password()
    return response


if __name__ == "__main__":
    ots = OTS('config.json')
    # Uncomment when testing
    app.debug = True
    app.run()
