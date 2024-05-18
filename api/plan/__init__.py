from flask import jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.model import Plan, User
from api.db import db

class Plans(Resource):
    @jwt_required()
    def get(self):
        plans = Plan.query.all()
        plan_list = [{'id': plan.id, 'name': plan.name, 'features': plan.features, 'price': plan.price} for plan in plans]
        return jsonify({'plans': plan_list})

class AddPlan(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if current_user.role != '2':
            return jsonify({'error': 'Unauthorized'})
        
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name is required')
        parser.add_argument('features', type=str, required=False)
        parser.add_argument('price', type=float, required=True, help='Price is required')
        args = parser.parse_args()

        new_plan = Plan(
            name=args['name'],
            features=args.get('features'),
            price=args['price']
        )

        db.session.add(new_plan)
        db.session.commit()

        return jsonify({'message': 'Plan added successfully', 'plan_id': new_plan.id})

class DeletePlan(Resource):
    @jwt_required()
    def delete(self, plan_id):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if current_user.role != 2:
            return jsonify({'error': 'Unauthorized'}), 401

        plan = Plan.query.get(plan_id)
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404

        db.session.delete(plan)
        db.session.commit()

        return jsonify({'message': 'Plan deleted successfully'})
