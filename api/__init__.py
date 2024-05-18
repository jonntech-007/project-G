from flask import Blueprint, jsonify
from flask_restful import Api

from api.login import Login, Logout, Register, VerifyOTP
from api.model import TokenBlacklist
from api.plan import AddPlan, DeletePlan, Plans
from api.task import Tasks
from api.time_entry import TimeEntryResource
from .resources import HelloWorld

api_bp = Blueprint('api', __name__)
api = Api(api_bp)


# Add API resources
api.add_resource(HelloWorld, '/hello')
api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
# api.add_resource(Tasks, '/test')
api.add_resource(VerifyOTP, '/verify-otp')
api.add_resource(Logout, '/logout')
api.add_resource(Tasks, '/tasks','/tasks/<int:task_id>')
api.add_resource(TimeEntryResource, '/tasks/<int:task_id>/time/<string:action>', '/tasks/<int:task_id>/time')
# Add new resources for managing plans
api.add_resource(Plans, '/plans')
api.add_resource(AddPlan, '/add_plan')
api.add_resource(DeletePlan, '/delete_plan/<int:plan_id>')

