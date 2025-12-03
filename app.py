from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///allulose_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class HungerEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    variant = db.Column(db.String(1), nullable=False)  # A or B
    allulose_time = db.Column(db.DateTime, nullable=False)
    hunger_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)

    # Confounding variables
    activity_level = db.Column(db.String(20))  # Low/Medium/High
    sleep_hours = db.Column(db.Float)
    sleep_quality = db.Column(db.Integer)  # 1-10
    stress_level = db.Column(db.Integer)  # 1-10
    concerta_timing = db.Column(db.String(50))
    water_intake_oz = db.Column(db.Integer)
    food_eaten = db.Column(db.Text)
    notes = db.Column(db.Text)

    is_baseline = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'variant': self.variant,
            'allulose_time': self.allulose_time.isoformat(),
            'hunger_time': self.hunger_time.isoformat(),
            'duration_minutes': self.duration_minutes,
            'activity_level': self.activity_level,
            'sleep_hours': self.sleep_hours,
            'sleep_quality': self.sleep_quality,
            'stress_level': self.stress_level,
            'concerta_timing': self.concerta_timing,
            'water_intake_oz': self.water_intake_oz,
            'food_eaten': self.food_eaten,
            'notes': self.notes,
            'is_baseline': self.is_baseline
        }

class SubjectiveRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    metric_type = db.Column(db.String(20), nullable=False)  # energy/clarity/mood/performance
    value = db.Column(db.Integer, nullable=False)  # 1-10
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'timestamp': self.timestamp.isoformat(),
            'metric_type': self.metric_type,
            'value': self.value,
            'notes': self.notes
        }

class GIEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    allulose_amount_g = db.Column(db.Integer, nullable=False)
    time_since_consumption_min = db.Column(db.Integer, nullable=False)
    symptoms = db.Column(db.Text, nullable=False)  # JSON array
    severity = db.Column(db.Integer, nullable=False)  # 1-10
    duration_minutes = db.Column(db.Integer)
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'timestamp': self.timestamp.isoformat(),
            'allulose_amount_g': self.allulose_amount_g,
            'time_since_consumption_min': self.time_since_consumption_min,
            'symptoms': json.loads(self.symptoms) if self.symptoms else [],
            'severity': self.severity,
            'duration_minutes': self.duration_minutes,
            'notes': self.notes
        }

class MealEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast/lunch/dinner/snack
    description = db.Column(db.Text, nullable=False)
    tags = db.Column(db.Text)  # JSON array of tags
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'timestamp': self.timestamp.isoformat(),
            'meal_type': self.meal_type,
            'description': self.description,
            'tags': json.loads(self.tags) if self.tags else [],
            'notes': self.notes
        }

class Settings(db.Model):
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value
        }

# Initialize database
with app.app_context():
    db.create_all()
    # Set default settings if they don't exist
    if not Settings.query.filter_by(key='experiment_week').first():
        db.session.add(Settings(key='experiment_week', value='1'))
    if not Settings.query.filter_by(key='active_timer').first():
        db.session.add(Settings(key='active_timer', value='null'))
    db.session.commit()

# Routes - Views
@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/hunger')
def hunger():
    return render_template('hunger.html')

@app.route('/ratings')
def ratings():
    return render_template('ratings.html')

@app.route('/meals')
def meals():
    return render_template('meals.html')

@app.route('/gi')
def gi():
    return render_template('gi.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

# API Endpoints - Hunger
@app.route('/api/hunger', methods=['GET', 'POST'])
def api_hunger():
    if request.method == 'GET':
        date_param = request.args.get('date')
        if date_param:
            target_date = datetime.fromisoformat(date_param).date()
            entries = HungerEntry.query.filter_by(date=target_date).all()
        else:
            entries = HungerEntry.query.order_by(HungerEntry.date.desc()).all()
        return jsonify([entry.to_dict() for entry in entries])

    elif request.method == 'POST':
        data = request.json
        entry = HungerEntry(
            date=datetime.fromisoformat(data['date']).date(),
            variant=data['variant'],
            allulose_time=datetime.fromisoformat(data['allulose_time']),
            hunger_time=datetime.fromisoformat(data['hunger_time']),
            duration_minutes=data['duration_minutes'],
            activity_level=data.get('activity_level'),
            sleep_hours=data.get('sleep_hours'),
            sleep_quality=data.get('sleep_quality'),
            stress_level=data.get('stress_level'),
            concerta_timing=data.get('concerta_timing'),
            water_intake_oz=data.get('water_intake_oz'),
            food_eaten=data.get('food_eaten'),
            notes=data.get('notes'),
            is_baseline=data.get('is_baseline', False)
        )
        db.session.add(entry)
        db.session.commit()
        return jsonify(entry.to_dict()), 201

@app.route('/api/hunger/<int:id>', methods=['DELETE'])
def delete_hunger(id):
    entry = HungerEntry.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return '', 204

# API Endpoints - Ratings
@app.route('/api/ratings', methods=['GET', 'POST'])
def api_ratings():
    if request.method == 'GET':
        date_param = request.args.get('date')
        if date_param:
            target_date = datetime.fromisoformat(date_param).date()
            ratings = SubjectiveRating.query.filter_by(date=target_date).all()
        else:
            ratings = SubjectiveRating.query.order_by(SubjectiveRating.timestamp.desc()).all()
        return jsonify([rating.to_dict() for rating in ratings])

    elif request.method == 'POST':
        data = request.json
        rating = SubjectiveRating(
            date=datetime.fromisoformat(data['date']).date(),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.utcnow().isoformat())),
            metric_type=data['metric_type'],
            value=data['value'],
            notes=data.get('notes')
        )
        db.session.add(rating)
        db.session.commit()
        return jsonify(rating.to_dict()), 201

@app.route('/api/ratings/<int:id>', methods=['DELETE'])
def delete_rating(id):
    rating = SubjectiveRating.query.get_or_404(id)
    db.session.delete(rating)
    db.session.commit()
    return '', 204

# API Endpoints - GI Events
@app.route('/api/gi', methods=['GET', 'POST'])
def api_gi():
    if request.method == 'GET':
        events = GIEvent.query.order_by(GIEvent.timestamp.desc()).all()
        return jsonify([event.to_dict() for event in events])

    elif request.method == 'POST':
        data = request.json
        event = GIEvent(
            date=datetime.fromisoformat(data['date']).date(),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.utcnow().isoformat())),
            allulose_amount_g=data['allulose_amount_g'],
            time_since_consumption_min=data['time_since_consumption_min'],
            symptoms=json.dumps(data['symptoms']),
            severity=data['severity'],
            duration_minutes=data.get('duration_minutes'),
            notes=data.get('notes')
        )
        db.session.add(event)
        db.session.commit()
        return jsonify(event.to_dict()), 201

@app.route('/api/gi/<int:id>', methods=['DELETE'])
def delete_gi(id):
    event = GIEvent.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    return '', 204

# API Endpoints - Meals
@app.route('/api/meals', methods=['GET', 'POST'])
def api_meals():
    if request.method == 'GET':
        date_param = request.args.get('date')
        if date_param:
            target_date = datetime.fromisoformat(date_param).date()
            meals = MealEntry.query.filter_by(date=target_date).order_by(MealEntry.timestamp.desc()).all()
        else:
            meals = MealEntry.query.order_by(MealEntry.timestamp.desc()).all()
        return jsonify([meal.to_dict() for meal in meals])

    elif request.method == 'POST':
        data = request.json
        meal = MealEntry(
            date=datetime.fromisoformat(data['date']).date(),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.utcnow().isoformat())),
            meal_type=data['meal_type'],
            description=data['description'],
            tags=json.dumps(data.get('tags', [])),
            notes=data.get('notes')
        )
        db.session.add(meal)
        db.session.commit()
        return jsonify(meal.to_dict()), 201

@app.route('/api/meals/<int:id>', methods=['DELETE'])
def delete_meal(id):
    meal = MealEntry.query.get_or_404(id)
    db.session.delete(meal)
    db.session.commit()
    return '', 204

# API Endpoints - Timer
@app.route('/api/timer', methods=['GET', 'POST', 'DELETE'])
def api_timer():
    if request.method == 'GET':
        timer = Settings.query.filter_by(key='active_timer').first()
        if timer and timer.value != 'null':
            return jsonify(json.loads(timer.value))
        return jsonify(None)

    elif request.method == 'POST':
        data = request.json
        timer = Settings.query.filter_by(key='active_timer').first()
        timer.value = json.dumps(data)
        db.session.commit()
        return jsonify(data), 201

    elif request.method == 'DELETE':
        timer = Settings.query.filter_by(key='active_timer').first()
        timer.value = 'null'
        db.session.commit()
        return '', 204

# API Endpoints - Settings
@app.route('/api/settings/week', methods=['GET', 'POST'])
def api_settings_week():
    if request.method == 'GET':
        setting = Settings.query.filter_by(key='experiment_week').first()
        return jsonify({'week': int(setting.value)})

    elif request.method == 'POST':
        data = request.json
        setting = Settings.query.filter_by(key='experiment_week').first()
        setting.value = str(data['week'])
        db.session.commit()
        return jsonify({'week': int(setting.value)})

# API Endpoints - Export/Import/Clear
@app.route('/api/export', methods=['GET'])
def api_export():
    data = {
        'hunger_entries': [e.to_dict() for e in HungerEntry.query.all()],
        'subjective_ratings': [r.to_dict() for r in SubjectiveRating.query.all()],
        'gi_events': [e.to_dict() for e in GIEvent.query.all()],
        'meal_entries': [m.to_dict() for m in MealEntry.query.all()],
        'settings': {s.key: s.value for s in Settings.query.all()},
        'export_date': datetime.utcnow().isoformat()
    }
    return jsonify(data)

@app.route('/api/import', methods=['POST'])
def api_import():
    data = request.json

    # Clear existing data
    HungerEntry.query.delete()
    SubjectiveRating.query.delete()
    GIEvent.query.delete()
    MealEntry.query.delete()

    # Import hunger entries
    for entry_data in data.get('hunger_entries', []):
        entry = HungerEntry(
            date=datetime.fromisoformat(entry_data['date']).date(),
            variant=entry_data['variant'],
            allulose_time=datetime.fromisoformat(entry_data['allulose_time']),
            hunger_time=datetime.fromisoformat(entry_data['hunger_time']),
            duration_minutes=entry_data['duration_minutes'],
            activity_level=entry_data.get('activity_level'),
            sleep_hours=entry_data.get('sleep_hours'),
            sleep_quality=entry_data.get('sleep_quality'),
            stress_level=entry_data.get('stress_level'),
            concerta_timing=entry_data.get('concerta_timing'),
            water_intake_oz=entry_data.get('water_intake_oz'),
            food_eaten=entry_data.get('food_eaten'),
            notes=entry_data.get('notes'),
            is_baseline=entry_data.get('is_baseline', False)
        )
        db.session.add(entry)

    # Import subjective ratings
    for rating_data in data.get('subjective_ratings', []):
        rating = SubjectiveRating(
            date=datetime.fromisoformat(rating_data['date']).date(),
            timestamp=datetime.fromisoformat(rating_data['timestamp']),
            metric_type=rating_data['metric_type'],
            value=rating_data['value'],
            notes=rating_data.get('notes')
        )
        db.session.add(rating)

    # Import GI events
    for event_data in data.get('gi_events', []):
        event = GIEvent(
            date=datetime.fromisoformat(event_data['date']).date(),
            timestamp=datetime.fromisoformat(event_data['timestamp']),
            allulose_amount_g=event_data['allulose_amount_g'],
            time_since_consumption_min=event_data['time_since_consumption_min'],
            symptoms=json.dumps(event_data['symptoms']),
            severity=event_data['severity'],
            duration_minutes=event_data.get('duration_minutes'),
            notes=event_data.get('notes')
        )
        db.session.add(event)

    # Import meal entries
    for meal_data in data.get('meal_entries', []):
        meal = MealEntry(
            date=datetime.fromisoformat(meal_data['date']).date(),
            timestamp=datetime.fromisoformat(meal_data['timestamp']),
            meal_type=meal_data['meal_type'],
            description=meal_data['description'],
            tags=json.dumps(meal_data.get('tags', [])),
            notes=meal_data.get('notes')
        )
        db.session.add(meal)

    # Import settings
    for key, value in data.get('settings', {}).items():
        setting = Settings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            db.session.add(Settings(key=key, value=value))

    db.session.commit()
    return jsonify({'message': 'Data imported successfully'}), 201

@app.route('/api/clear', methods=['POST'])
def api_clear():
    HungerEntry.query.delete()
    SubjectiveRating.query.delete()
    GIEvent.query.delete()
    MealEntry.query.delete()

    # Reset settings
    timer = Settings.query.filter_by(key='active_timer').first()
    timer.value = 'null'
    week = Settings.query.filter_by(key='experiment_week').first()
    week.value = '1'

    db.session.commit()
    return jsonify({'message': 'All data cleared'}), 200

# API Endpoints - Stats
@app.route('/api/stats', methods=['GET'])
def api_stats():
    # Get today's date
    today = datetime.utcnow().date()

    # Hunger stats
    baseline_entries = HungerEntry.query.filter_by(is_baseline=True).all()
    allulose_entries = HungerEntry.query.filter_by(is_baseline=False).all()

    baseline_avg = sum(e.duration_minutes for e in baseline_entries) / len(baseline_entries) if baseline_entries else 0
    allulose_avg = sum(e.duration_minutes for e in allulose_entries) / len(allulose_entries) if allulose_entries else 0

    # Today's ratings
    today_ratings = SubjectiveRating.query.filter_by(date=today).all()
    ratings_by_type = {}
    for metric in ['energy', 'clarity', 'mood', 'performance']:
        metric_ratings = [r.value for r in today_ratings if r.metric_type == metric]
        ratings_by_type[metric] = sum(metric_ratings) / len(metric_ratings) if metric_ratings else 0

    # GI tolerance
    gi_events = GIEvent.query.all()
    gi_threshold = None
    if gi_events:
        # Find the lowest amount that caused discomfort
        amounts = [e.allulose_amount_g for e in gi_events if e.severity >= 5]
        gi_threshold = min(amounts) if amounts else None

    return jsonify({
        'baseline_avg_minutes': round(baseline_avg, 1),
        'allulose_avg_minutes': round(allulose_avg, 1),
        'improvement_minutes': round(allulose_avg - baseline_avg, 1),
        'today_ratings': ratings_by_type,
        'gi_threshold': gi_threshold,
        'total_entries': {
            'hunger': len(baseline_entries) + len(allulose_entries),
            'ratings': SubjectiveRating.query.count(),
            'gi_events': len(gi_events),
            'meals': MealEntry.query.count()
        }
    })

# API Endpoints - Days
@app.route('/api/days', methods=['GET'])
def api_days():
    # Get all unique dates from all tables
    hunger_dates = db.session.query(HungerEntry.date).distinct().all()
    rating_dates = db.session.query(SubjectiveRating.date).distinct().all()
    gi_dates = db.session.query(GIEvent.date).distinct().all()
    meal_dates = db.session.query(MealEntry.date).distinct().all()

    all_dates = set()
    for date_tuple in hunger_dates:
        all_dates.add(date_tuple[0].isoformat())
    for date_tuple in rating_dates:
        all_dates.add(date_tuple[0].isoformat())
    for date_tuple in gi_dates:
        all_dates.add(date_tuple[0].isoformat())
    for date_tuple in meal_dates:
        all_dates.add(date_tuple[0].isoformat())

    return jsonify(sorted(list(all_dates), reverse=True))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
