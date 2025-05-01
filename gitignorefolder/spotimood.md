# 📄 Functional Requirements Document  
## Project: **SpotyMood**  
_Last updated: May 1, 2025_

---

## 1. 🎯 Purpose
SpotyMood is a web application that visualizes the listening habits of Spotify users by analyzing mood-related audio features (e.g., valence, energy) of their favorite tracks. It supports multiple users, retrieves and caches song data, and presents visual summaries of mood evolution using a color-coded interface.

---

## 2. 👥 User Management and Authentication

### FR1.1 – Spotify Authentication
The application shall allow users to authenticate securely using their Spotify account via OAuth 2.0.

### FR1.2 – Multi-User IAM Support
The system shall support multiple users and ensure data isolation per user through proper Identity and Access Management (IAM) practices.

### FR1.3 – User Profile Storage
Upon login, the system shall retrieve and store:
- Spotify User ID  
- Display name  
- Top artists (last 4 weeks, 6 months, all time)  
- Top songs  
- Top albums  

---

## 3. 🔗 Spotify Integration and Listening History

### FR2.1 – Initial Data Fetch
The application shall retrieve the user’s last 50 listened tracks via the Spotify API.

### FR2.2 – History Accumulation
To build a longer history, the system shall periodically refresh the latest 50 tracks and avoid duplicates to construct a growing archive of listening activity.

### FR2.3 – Cached Song Metadata and Audio Features
The application shall:
- Check the cache/database before retrieving song data.
- If found, reuse the cached version.
- If not found, fetch and store:
  - Audio features (valence, energy, danceability, etc.)
  - Metadata (title, artist, album, duration)
  - Additional songs from the album
  - Artist metadata (biography or genre, if available)
  - **Lyrics** from any online source (e.g., Genius, Lyrics.ovh, Musixmatch)

### FR2.4 – Listening History Views
Users shall access:
- Last 50 songs  
- Full listening history  
- Top songs, artists, albums (per month, 6-months, all-time)

---

## 4. 😊 Mood Analysis and Visualization

### FR3.1 – Mood Computation
The app shall compute a mood classification for each track using Spotify’s valence and energy attributes.

### FR3.2 – Mood Evolution Over Time
Users shall view mood changes over time.  
**Preferred time groupings include:**
- Daily
- Weekly
- Monthly
- **4-hour blocks** (00:00–04:00, 04:00–08:00, etc.)

### FR3.3 – Lyrics and Mood Topics
The app shall analyze lyrics (when available) and extract mood themes (e.g., heartbreak, nostalgia, confidence).

### FR3.4 – Friends' Mood Comparison
Users may link with other users to compare mood evolution and trends.

---

## 5. 📊 Statistics and Graphs

### FR4.1 – Usage Statistics
The app shall calculate:
- Songs played per time period  
- Average valence and energy  
- Most common moods

### FR4.2 – Visualizations
Display:
- Mood evolution (line/area graph)
- Histograms of mood frequencies
- Listening heatmaps by day/hour
- Mood breakdown pie charts
- Lyric clouds by mood

### FR4.3 – Mood Color Graph
Mood colors on graphs follow this valence-based color map:

| Valence Range | Mood       | Hex Code  |
|---------------|------------|-----------|
| 0.0 – 0.1     | Depressed  | `#1f1f7a` |
| 0.1 – 0.2     | Sad        | `#233f7a` |
| 0.2 – 0.3     | Melancholy | `#517da2` |
| 0.3 – 0.4     | Calm       | `#468b9f` |
| 0.4 – 0.5     | Neutral    | `#8fc4af` |
| 0.5 – 0.6     | Content    | `#b0d98f` |
| 0.6 – 0.7     | Optimistic | `#dde768` |
| 0.7 – 0.8     | Happy      | `#fdd757` |
| 0.8 – 0.9     | Joyful     | `#fba03c` |
| 0.9 – 1.0     | Ecstatic   | `#fc4c4e` |

---

## 6. 🖥️ Web Interface and Pages

### FR6.1 – Pages and Navigation
Main pages include:
- **Full History**: Filterable song archive
- **Last 50 Songs**: Recent mood map
- **Top Songs**: Ranked by valence, energy, play count
- **Mood Histogram**: Mood color histogram of valence ranges

### FR6.2 – Responsiveness
The UI shall adapt to all screen sizes and devices.

### FR6.3 – Interactivity
Users can:
- Hover/click graph elements  
- Filter by time, mood, artist  
- Export visuals to image or CSV

---

## 7. ⚙️ Infrastructure and Deployment

### FR7.1 – Dockerization
All components (backend, frontend, database) shall be containerized using Docker.

### FR7.2 – Service Orchestration
Use Docker Compose to coordinate containerized services.

### FR7.3 – Secure Storage
OAuth tokens, user data, and analytics must be securely stored and encrypted as needed.

---

## 8. 🧩 Other Functional & UX Features

### FR8.1 – API Error Handling
Implement retries, backoff, and user notifications for:
- Spotify API errors
- Token expiration
- Lyrics provider downtime

### FR8.2 – User Preferences
Users may customize:
- Mood range thresholds  
- Preferred time grouping (e.g., half-day vs. 4-hour)  
- Toggle lyrics analysis

### FR8.3 – Onboarding
New users see a guided intro if no listening history is available.

### FR8.4 – Data Deletion
Users may request deletion of:
- All saved listening data  
- Cached song info  
- Spotify tokens

---

## 9. 🚀 Non-Functional Requirements (NFRs)

### NFR1 – Performance
- The system must support **at least 100 concurrent users** with an average backend response time of **under 2 seconds**.
- All page loads (dashboard views) must complete in **under 1.5 seconds** on a broadband connection (25 Mbps or more).

### NFR2 – Scalability
- The app must support horizontal scaling via Docker services.

### NFR3 – Security
- Use HTTPS for all frontend/backend communication.
- Store OAuth tokens encrypted at rest.
- Follow Spotify’s API usage policy.

### NFR4 – Maintainability
- Code must be modular, with separation between UI, logic, and storage layers.
