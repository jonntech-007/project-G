


from datetime import datetime
import sre_parse
from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_restful import Resource, reqparse
from api.db import db
from api.model import Task, User


class Tasks(Resource):
    @jwt_required()
    def get(self):
        # Extract the user ID and role from the JWT
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()

        # Check if user exists
        if not user:
            return jsonify({'message': 'User not found'})

        # Get user role
        user_role = user.role

        if user_role == '2':
            # If user role is 2, get tasks where the user is the reporter
            tasks = Task.query.filter_by().all()
        elif user_role == '0':
            # If user role is 0, get tasks where the user is the assignee
            tasks = Task.query.filter_by(assignee_id=user_id).all()
        elif user_role == '1':
            tasks = Task.query.filter_by(reporter_id=user_id).all()

        else:
            # If user role is neither 2 nor 0, return unauthorized
            return jsonify({'message': 'Unauthorized access'})

        # Serialize the tasks
        tasks_list = []
        for task in tasks:
            task_data = {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'assignee_id': task.assignee_id,
                'reporter_id': task.reporter_id,
                'created_date': task.created_date,
                'updated_date': task.updated_date
            }
            tasks_list.append(task_data)

        return jsonify({'tasks': tasks_list})
    
    @jwt_required()
    def post(self):
        claims = get_jwt()
        user_role = claims.get('user_role')
        user_id = claims.get('user_id')
        print("user_role", user_role==1)

        if user_role not in ['1', '2']:
            return jsonify({'error': 'Unauthorized'})

        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True, help='Title is required')
        parser.add_argument('description', type=str, required=False)
        parser.add_argument('status', type=str, required=True, help='Status is required')
        parser.add_argument('priority', type=str, required=True, help='Priority is required')
        parser.add_argument('assignee_id', type=int, required=True, help='Assignee ID is required')
        args = parser.parse_args()

        new_task = Task(
            title=args['title'],
            description=args.get('description'),
            status=args['status'],
            priority=args['priority'],
            assignee_id=args['assignee_id'],
            reporter_id=user_id,
            created_date=datetime.utcnow(),
            updated_date=datetime.utcnow()
        )

        db.session.add(new_task)
        db.session.commit()

        return jsonify({'message': 'Task created successfully', 'task': new_task.id})
    
    @jwt_required()
    def put(self, task_id):
        claims = get_jwt()
        user_role = claims.get('user_role')
        user_id = claims.get('user_id')
        # Find the task by ID
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return jsonify({'error': 'Task not found'})

        # Role-based permission checks
        if user_role == '2':
            # Admin can change any task
            pass
        elif user_role == '1':
            # Reporter can only change their own tasks
            if task.reporter_id != user_id:
                return jsonify({'error': 'Unauthorized'})
        else:
            return jsonify({'error': 'Unauthorized'})

        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=False)
        parser.add_argument('description', type=str, required=False)
        parser.add_argument('status', type=str, required=False)
        parser.add_argument('priority', type=str, required=False)
        parser.add_argument('assignee_id', type=int, required=False)
        args = parser.parse_args()

        if args['title']:
            task.title = args['title']
        if args['description']:
            task.description = args['description']
        if args['status']:
            task.status = args['status']
        if args['priority']:
            task.priority = args['priority']
        if args['assignee_id']:
            task.assignee_id = args['assignee_id']

        task.updated_date = datetime.utcnow()
        db.session.commit()

        return jsonify({'message': 'Task updated successfully'})

    @jwt_required()
    def patch(self, task_id):
        claims = get_jwt()
        user_role = claims.get('user_role')
        user_id = claims.get('user_id')


        # Find the task by ID
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return jsonify({'error': 'Task not found'})

        # Role-based permission checks
        if user_role == '0':
            # Assignee can only change the status of their own tasks
            if task.assignee_id != user_id:
                return jsonify({'error': 'Unauthorized'})
        parser = reqparse.RequestParser()
        parser.add_argument('status', type=str, required=True, help='Status is required')
        args = parser.parse_args()

        task.status = args['status']
        task.updated_date = datetime.utcnow()
        db.session.commit()

        return jsonify({'message': 'Task status updated successfully'})