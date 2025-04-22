import os
from flask import Flask
from flask_cors import CORS

from Controllers.reservation_controller import reservations_bp

app = Flask(
  __name__,
  static_folder='images',       # serve files from ./images
  static_url_path='/images'     # mount them at /images
)
CORS(app)
app.secret_key = os.urandom(24)

app.register_blueprint(reservations_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)