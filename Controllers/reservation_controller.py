from flask import Blueprint, request, session, jsonify
from Handlers.Reservations.oauth2callback import OAuth2CallbackHandler
from Handlers.Reservations.BookReservation import BookReservationHandler
import json

reservations_bp = Blueprint('reservations', __name__)

@reservations_bp.route('/oauth2callback', methods=['GET'])
def oauth2callback():
    oauth_handler = OAuth2CallbackHandler()
    code = request.args.get('code')
    state = request.args.get('state')
    if not code or not state:
        return jsonify({'error': 'Missing required parameters'}), 400
    return oauth_handler.handle_callback(code, state)

@reservations_bp.route('/book-reservation', methods=['POST'])
def book_reservation():
    book_reservation_handler = BookReservationHandler()
    data = request.get_json()
    return book_reservation_handler.book_reservation(data)


