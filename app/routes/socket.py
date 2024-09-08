from app import socketio
from flask import Blueprint, request

socket_routes = Blueprint('socket', __name__)

@socketio.on('connect')
def handle_connect():
    client = request.sid # as in the older answer
    print('Client connected with session ID!:', client)
