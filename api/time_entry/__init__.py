from datetime import datetime
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse
from api.db import db
from api.model import Task, TimeEntry, User

class TimeEntryResource(Resource):
    @jwt_required()
    def post(self, task_id, action):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()

        if not user:
            return jsonify({'message': 'User not found'})

        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return jsonify({'message': 'Task not found'})

        if action == 'start':
            ongoing_entry = TimeEntry.query.filter_by(task_id=task_id, end_time=None).first()
            if ongoing_entry:
                return jsonify({'message': 'Task already started and not ended'})

            new_entry = TimeEntry(task_id=task_id, start_time=datetime.utcnow(), end_time=None)
            db.session.add(new_entry)
            db.session.commit()

            return jsonify({'message': 'Task started', 'time_entry_id': new_entry.id})

        elif action == 'end':
            ongoing_entry = TimeEntry.query.filter_by(task_id=task_id, end_time=None).first()
            if not ongoing_entry:
                return jsonify({'message': 'No ongoing task found to end'})

            ongoing_entry.end_time = datetime.utcnow()
            db.session.commit()

            return jsonify({'message': 'Task ended', 'time_entry_id': ongoing_entry.id})

        else:
            return jsonify({'message': 'Invalid action'})

    @jwt_required()
    def get(self, task_id):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()

        if not user:
            return jsonify({'message': 'User not found'})

        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return jsonify({'message': 'Task not found'})

        time_entries = TimeEntry.query.filter_by(task_id=task_id).all()
        total_time = sum([(entry.end_time - entry.start_time).total_seconds() for entry in time_entries if entry.end_time], 0)

        return jsonify({'total_time_seconds': total_time})
