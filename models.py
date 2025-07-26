from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(100), unique=True, nullable=False)  # Unique hardware ID
    user_name = db.Column(db.String(100))  # Given by user
    last_latitude = db.Column(db.Float)
    last_longitude = db.Column(db.Float)
    last_updated = db.Column(db.DateTime)

class Snapshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Snapshot_name = db.Column(db.String(100), nullable=True)
    device_id = db.Column(db.String(100), db.ForeignKey('device.device_id'), nullable=False)
    Snapshot_data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    device = db.relationship('Device', backref=db.backref('snapshots', lazy=True))