# Changelog

## [Updated] - 2025-12-01

### Added - Time-of-Day Visualization for Hunger Entries

#### New Feature: Hunger Delay Chart
- **Location**: Hunger Tracking page ([hunger.html](templates/hunger.html))
- **What it does**: Displays a line chart showing when you logged hunger entries throughout the day and the corresponding hunger delay duration

#### Chart Details:
- **X-axis**: Time of day when entries were logged (e.g., 8am, 2pm, 6pm)
- **Y-axis**: Hunger delay duration in hours and minutes
- **Data Series**:
  - 🔵 **Blue line**: Baseline entries (no Allulose)
  - 🟢 **Green line**: Variant A (Meal + Allulose)
  - 🟠 **Orange line**: Variant B (Allulose only)

#### How It Works:
1. **Multiple entries per day**: Log entries at 8am, 2pm, 6pm - each will appear on the chart
2. **Time tracking**: The chart uses the `hunger_time` field (when you logged feeling hungry)
3. **Visual patterns**: See how hunger delay changes throughout the day
4. **Compare variants**: Baseline vs Allulose variants are shown in different colors

#### Entry Display Enhancement:
- Each entry now shows "Logged at: [time]" to clearly indicate when the entry was recorded
- Full timeline: "Logged at: 2pm | Started: 12pm → Hungry: 2pm"

#### Use Cases:
- **Pattern recognition**: Notice if Allulose works better at certain times of day
- **Timing optimization**: Identify optimal times to consume Allulose
- **Day comparison**: Navigate between days to see different daily patterns
- **Variant comparison**: Visually compare how different variants perform throughout the day

#### Example Scenario:
You log three hunger entries on Monday:
1. 8am: Variant A, 90-minute delay
2. 2pm: Variant A, 120-minute delay
3. 6pm: Baseline, 45-minute delay

The chart will show three data points at those times, with the first two connected by a green line (Variant A) and the third as a blue point (Baseline).

#### Technical Details:
- Uses Chart.js time-series visualization
- Automatically shows/hides based on available data
- Dark theme compatible with custom colors
- Responsive design works on mobile and desktop
- Hover over points to see exact times and durations

---

## Initial Release - 2025-11-28

### Core Features
- Hunger onset timer with variant selection
- Subjective ratings (Energy, Clarity, Mood, Physical)
- GI events logger with tolerance threshold calculation
- Dashboard with insights and quick actions
- Settings with data export/import for device syncing
- Dark theme, mobile-first responsive design
- SQLite database with comprehensive tracking
