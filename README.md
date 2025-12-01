# Allulose Experiment Tracker

A mobile-friendly web application for tracking the health effects of Allulose consumption as a personal experiment.

## Features

### 🍽️ Hunger Onset Timer
- Start timer with variant selection (Meal + Allulose or Allulose only)
- Live elapsed time display
- Comprehensive logging of confounding variables
- Baseline mode for Week 1 control data
- Manual entry for backdating

### ⭐ Subjective Ratings
- Quick-rate 4 metrics: Energy, Clarity, Mood, Physical Performance
- 1-10 slider interface
- Interactive Chart.js time-series visualization
- Day-by-day historical view

### 🔔 GI Events Logger
- Event-based logging (only when discomfort occurs)
- Multiple symptom tracking
- Severity and duration measurement
- Automatic tolerance threshold calculation

### 📊 Dashboard
- Real-time active timer display
- Quick action buttons
- Today's stats at a glance
- Experiment insights (baseline vs Allulose comparison)
- GI threshold warnings

### ⚙️ Settings & Data Management
- Experiment week tracking
- Export data as JSON
- Import data for device syncing
- Clear all data with confirmation
- Statistics overview

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Tech Stack

- **Backend**: Python, Flask, Flask-SQLAlchemy
- **Frontend**: HTML/CSS/JavaScript (vanilla)
- **Database**: SQLite
- **Charts**: Chart.js
- **Design**: Dark theme, mobile-first responsive

## Usage

### Week 1 - Baseline
1. Set experiment week to "Week 1" in Settings
2. Use the Hunger page with "Baseline Mode" toggle ON
3. Log hunger entries without Allulose to establish baseline

### Week 2+ - With Allulose
1. Update experiment week in Settings
2. Use "Start Timer" on Dashboard when consuming Allulose
3. Click "I'm Hungry" when hunger sets in
4. Fill in confounding variables
5. Log subjective ratings throughout the day
6. Log GI events only if discomfort occurs

### Data Syncing
1. Export data from Settings page
2. Save JSON file to cloud storage or transfer to another device
3. Import on new device to continue tracking

## Database Schema

### HungerEntry
- Hunger onset timing and duration
- Variant (A or B) or baseline flag
- Confounding variables: activity, sleep, stress, Concerta timing, water, food, notes

### SubjectiveRating
- Metric type (energy/clarity/mood/performance)
- 1-10 value
- Timestamp for time-series analysis

### GIEvent
- Allulose amount and timing
- Symptoms (multiple selection)
- Severity (1-10) and duration
- Notes

### Settings
- Experiment week
- Active timer state

## Design Philosophy

- **ADHD-Friendly**: Quick actions, minimal friction, flexible logging
- **Mobile-First**: Responsive design optimized for phone use
- **No Rigid Schedules**: Log anytime, backdate entries
- **Event-Based GI Tracking**: Only log when problems occur
- **Dark Theme**: Easy on the eyes with green accent (#4ade80)

## License

Personal use project.
