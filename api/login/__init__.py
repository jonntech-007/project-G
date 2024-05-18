from flask import app, config, current_app, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from flask_restful import Resource, reqparse, abort
import pyotp
from flask_mail import Message
from api.mail import mail
from api.model import TokenBlacklist, User
from api.db import db  # Import the db object from your database setup file
from flask import current_app


# class AuthenticatedResource(Resource):
#     def dispatch_request(self, *args, **kwargs):
#         # Extract API key from request headers
#         api_key = request.headers.get('API-Key')

#         # Verify API key (replace 'your_api_key' with your actual API key)
#         if api_key != '6969':
#             return jsonify({'error': 'Unauthorized'})

#         return super().dispatch_request(*args, **kwargs)


class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='Email is required')
        parser.add_argument('password', type=str, required=True, help='Password is required')
        parser.add_argument('role', type=int, required=True, help='Role is required (0, 1, or 2)')
        args = parser.parse_args()

        email = args['email']
        password = args['password']
        role = args['role']

        # Ensure role is either 0, 1, or 2
        if role not in [0, 1, 2]:
            return jsonify({'error': 'Role must be either 0, 1, or 2'})

        # Check if the user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already exists'})

        # If role is 2, check for admin secret key
        if role == 2:
            admin_secret_key = request.headers.get('Admin-Secret-Key')
            print('oni: omiwa',current_app.config)
            if admin_secret_key != current_app.config.get('ADMIN_SECRET_KEY'):
                return jsonify({'error': 'Unauthorized'})

        # Create a new user
        new_user = User(email=email, role=role)
        new_user.hash_password(password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully'})

    def get(self):
        return {'hello': 'boom baam'}


class SendOTP(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'message': 'User not found'})

        # Generate OTP
        user.otp = pyotp.random_base32()[:6]
        db.session.commit()

        # Send OTP via email
        msg = Message('Your OTP Code', recipients=[email])
        msg.body = f'Your OTP code is {user.otp}'
        mail.send(msg)
        return jsonify({'message': 'OTP sent successfully'})


class VerifyOTP(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        otp = data['otp']

        user = User.query.filter_by(email=email).first()
        if user and user.otp == otp:
            # Clear the OTP after successful verification
            user.otp = None
            db.session.commit()

            # Generate access token with additional claims
            additional_claims = {"user_role": user.role, "email": user.email, "user_id": user.id}
            access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
            return jsonify({'message': 'OTP verified', 'access_token': access_token})
        else:
            return jsonify({'message': 'Invalid OTP'})


class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('password', type=str,
                            required=True, help='Username is required')
        parser.add_argument('email', type=str, required=True,
                            help='Email is required')
        args = parser.parse_args()

        email = args['email']
        password = args['password']

        # Find the user by email
        user = User.query.filter_by(email=email).first()

        if user and user.verify_password(password):
            # Send OTP to user's email
            otp = pyotp.random_base32()[:6]
            user.otp = otp
            db.session.commit()
            print("user opt", otp)

            # Send OTP via email
            msg = Message('Your OTP Code', recipients=[email])
            msg.body = f'Your OTP code is {otp}'
            mail.send(msg)

            return jsonify({'message': 'OTP sent to email'})
        else:
            return jsonify({'message': 'Invalid email or password', 'code': 2})


# class Tasks(Resource):
#     @jwt_required()
#     def get(self):
#         # Extract the user ID from the JWT
#         user_id = get_jwt_identity()
#         user = User.query.filter_by(id=user_id).first()

#         # Check if user exists
#         if user:
#             return jsonify({'message': 'User found', 'name': user.email})
#         else:
#             return jsonify({'message': 'User not found'})


class Logout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        revoked_token = TokenBlacklist(jti=jti)
        db.session.add(revoked_token)
        db.session.commit()
        return jsonify({'message': 'Successfully logged out'})
