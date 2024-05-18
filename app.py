#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:rootpassword@localhost/sampledb'
#db = SQLAlchemy(app)

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from api import api_bp
from api.db import db
from api.model import TokenBlacklist
from config import Config
from api.mail import mail

app = Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app)
mail = mail.init_app(app)
print('oni: b is', app.config)
db.init_app(app)

# Create tables if they do not exist
with app.app_context():
    db.create_all()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    token = TokenBlacklist.query.filter_by(jti=jti).first()
    return token is not None

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({'message': 'Token has been revoked'})

app.register_blueprint(api_bp, url_prefix='/api')



if __name__ == '__main__':
    app.run(port=8000,host="0.0.0.0", debug=False)


