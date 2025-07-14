from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Device, Snapshot
from config import Config
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)


db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

@app.route('/')
def home():
    return "Device Tracker API Running "

@app.route('/register_device', methods=['POST'])
def register_device():
    data = request.json
    device_id = data.get('device_id')
    user_name = data.get('user_name')

    if not device_id:
        return jsonify({"error": "Device ID is required"}), 400

    device = Device.query.filter_by(device_id=device_id).first()
    if device:
        device.user_name = user_name or device.user_name
    else:
        device = Device(device_id=device_id, user_name=user_name)
        db.session.add(device)

    db.session.commit()
    return jsonify({"message": "Device registered successfully"})

@app.route('/update_location', methods=['POST'])
def update_location():
    data = request.json
    device_id = data.get('device_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not all([device_id, latitude, longitude]):
        return jsonify({"error": "device_id, latitude and longitude are required"}), 400

    device = Device.query.filter_by(device_id=device_id).first()
    if not device:
        return jsonify({"error": "Device not registered"}), 404

    device.last_latitude = latitude
    device.last_longitude = longitude
    device.last_updated = datetime.utcnow()

    db.session.commit()
    return jsonify({"message": "Location updated successfully"})

@app.route('/snapshot', methods=['POST'])
def save_snapshot():
    data = request.get_json()
    device_id = data.get('device_id')
    snapshot_data = data.get('snapshot_data')

    if not all([device_id, snapshot_data]):
        return jsonify({"error": "device_id and snapshot_data are required"}), 400

    device = Device.query.filter_by(device_id=device_id).first()
    if not device:
        return jsonify({"error": "Device not registered"}), 404

    snapshot = Snapshot(device_id=device_id, Snapshot_data=snapshot_data)
    db.session.add(snapshot)
    db.session.commit()

    return jsonify({"message": "Snapshot saved successfully"})

@app.route('/get_snapshots/<device_id>', methods=['GET'])
def get_snapshots(device_id):
    Snapshots = Snapshot.query.filter_by(device_id=device_id).order_by(Snapshot.created_at.desc()).all()
    return jsonify({
        "snapshots": [
            {
                "id": snapshot.id,
                "snapshot_data": snapshot.Snapshot_data,
                "created_at": snapshot.created_at.isoformat()
            } for snapshot in Snapshots
        ]
    })

@app.route('/delete_snapshot/<int:snapshot_id>', methods=['DELETE'])
def delete_snapshot(snapshot_id):
    snapshot = Snapshot.query.get(snapshot_id)
    if not snapshot:
        return jsonify({"error": "Snapshot not found"}), 404
    
    try:
        db.session.delete(snapshot)
        db.session.commit()
        return jsonify({"message": "Snapshot deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/device_info/<device_id>', methods=['GET'])
def device_info(device_id):
    device = Device.query.filter_by(device_id=device_id).first()
    if not device:
        return jsonify({"error": "Device not found"}), 404

    return jsonify({
        "device_id": device.device_id,
        "user_name": device.user_name,
        "last_latitude": device.last_latitude,
        "last_longitude": device.last_longitude,
        "last_updated": device.last_updated.isoformat() if device.last_updated else None
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

