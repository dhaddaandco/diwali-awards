# 🏆 DCO Awards Live Polling System

A real-time interactive polling application built with Flask and SocketIO, perfect for live award ceremonies and team events!

## ✨ Features

- **Real-time Voting**: Live voting with instant updates
- **Host Controls**: Admin panel for managing polls and questions
- **Live Results**: Auto-updating bar charts with beautiful visualizations
- **30 Fun Award Categories**: Pre-loaded with creative award ideas
- **Responsive Design**: Works on desktop, tablet, and mobile
- **No Cost**: Runs on Render's free tier

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd dco-awards
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   - Home: http://localhost:5000
   - Admin: http://localhost:5000/admin
   - Vote: http://localhost:5000/vote
   - Results: http://localhost:5000/results

### Deploy to Render

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Connect to Render**
   - Go to [render.com](https://render.com)
   - Create a new Web Service
   - Connect your GitHub repository
   - Use these settings:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py`
     - **Environment**: Python 3

3. **Deploy!**
   - Click "Deploy" and wait for deployment to complete
   - Your app will be available at `https://your-app-name.onrender.com`

## 🎮 How to Use

### For Hosts (Admin Panel)
1. Go to `/admin` page
2. Select an award category from the list
3. Click "Start Current Poll" to begin voting
4. Monitor votes in real-time
5. Click "Next Question" to move to the next award
6. Click "End Poll" to stop current voting

### For Audience (Voting)
1. Go to `/vote` page
2. Wait for the host to start a poll
3. Click on your favorite team member's name
4. Change your vote anytime before the poll ends
5. Watch live results at `/results`

### For Viewers (Results)
1. Go to `/results` page
2. Watch real-time bar charts update
3. See who's winning as votes come in
4. View final results when poll ends

## 🏆 Award Categories

The app comes pre-loaded with 30 fun award categories:

1. Most Likely to Survive a Zombie Apocalypse
2. Best Coffee Addiction
3. Most Creative Excuse for Being Late
4. Best Zoom Background
5. Most Likely to Win a Karaoke Contest
6. Best Desk Decoration
7. Most Likely to Bring Snacks to Every Meeting
8. Best Email Signature
9. Most Likely to Remember Everyone's Birthday
10. Best PowerPoint Animation Skills
...and 20 more!

## 🛠️ Technical Details

- **Backend**: Flask with SocketIO for real-time communication
- **Frontend**: HTML, CSS, JavaScript with Chart.js
- **Real-time**: WebSocket connections for live updates
- **Styling**: Modern UI with light green theme
- **Charts**: Beautiful bar charts with winner highlighting
- **Responsive**: Mobile-friendly design

## 📱 Pages

- **`/`** - Home page with instructions and award list
- **`/admin`** - Host controls for managing polls
- **`/vote`** - Audience voting interface
- **`/results`** - Live results with charts

## 🔧 Customization

### Adding Team Members
Edit the `teamMembers` array in `templates/vote.html` to include your team:

```javascript
const teamMembers = [
    "Your Team Member 1",
    "Your Team Member 2",
    // ... add more names
];
```

### Modifying Award Categories
Edit the `awards` list in `app.py`:

```python
awards = [
    "Your Custom Award 1",
    "Your Custom Award 2",
    # ... add more awards
]
```

### Changing Colors
Modify the CSS variables in `templates/base.html` to match your brand colors.

## 🚀 Deployment Options

### Render (Recommended - Free)
- Automatic deployments from GitHub
- Free tier available
- Easy setup with `render.yaml`

### Heroku
- Add `Procfile` (included)
- Set environment variables
- Deploy with Git

### Other Platforms
- Any platform supporting Python/Flask
- Ensure WebSocket support for real-time features

## 📞 Support

For issues or questions:
1. Check the console for error messages
2. Ensure all dependencies are installed
3. Verify WebSocket connections are working
4. Check browser compatibility

## 🎉 Enjoy Your Awards!

Have fun with your team awards ceremony! The app is designed to be simple, engaging, and memorable. Customize it to fit your team's personality and enjoy the real-time voting experience!

---

Built with ❤️ for DCO Awards | Powered by Flask & SocketIO

