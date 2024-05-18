from flask_restful import Resource
from flask_mail import Message
from .mail import mail



from api.model import User
# from models import User

class HelloWorld(Resource):
    def get(self):
        users = User.query.all()
        msg = Message('Your OTP Code', recipients=['ajaychipmunk@gmail.com'])
        msg.body = f'Your OTP code is 123'
        mail.send(msg)
        print(users)
        return {'hello': 'world'}

