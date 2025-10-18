from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dco_awards_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state for the polling system
current_question = None
question_index = 0
votes = {}
is_polling_active = False
total_votes = 0

# 31 DCO Awards with 4 options each
awards = [
    "DCO's Bhukhad",
    "DCO's Late Latif", 
    "DCO's Bheja Fry",
    "DCO's Chapad Chapad",
    "DCO's Goli Master",
    "DCO's Narad Muni",
    "DCO's Bindas Insaan",
    "DCO's Most Sanskari",
    "DCO's Kamchor",
    "DCO's Chupa Rustom",
    "DCO's Ladaku",
    "DCO's MF Husain",
    "DCO's Dancer",
    "DCO's Gyani",
    "DCO's Influencer",
    "DCO's Style Icon",
    "DCO's Scariest Manager",
    "DCO's Chill Manager",
    "DCO's Star (All-Rounder)",
    "DCO's Chai Lover",
    "DCO's Sabka Dost, Kaam Ke Time Ghost",
    "DCO's Phone Pe Hi Busy",
    "DCO's 2-Min Break = 2-Hour Walk",
    "DCO's Deadline Warrior",
    "DCO's Tech Guru",
    "DCO's Fitness Freak",
    "DCO's Drama Queen/King",
    "DCO's Gumnaam",
    "DCO's Workholic",
    "DCO's Most Punctual",
    "DCO's Strongest Pillar"
]

# Award intro descriptions
award_intros = {
    "DCO's Bhukhad": "Always hungry",
    "DCO's Late Latif": "Jo kabhi time pe nahi aata",
    "DCO's Bheja Fry": "Asks 10 questions where 1 would do",
    "DCO's Chapad Chapad": "Keeps the office alive with unlimited commentary",
    "DCO's Goli Master": "Promises treats faster than you can say \"party,\" but kabhi deta nahi!",
    "DCO's Narad Muni": "Knows every gossip before it's even gossip.",
    "DCO's Bindas Insaan": "Cool, carefree, and never stressed — even during audits.",
    "DCO's Most Sanskari": "DCO's Most Sanskari",
    "DCO's Kamchor": "A master at looking busy while doing absolutely nothing.",
    "DCO's Chupa Rustom": "Secret keeper.",
    "DCO's Ladaku": "Always ready to debate - even with Google!",
    "DCO's MF Husain": "Turns every whiteboard into a work of art.",
    "DCO's Dancer": "Can groove anywhere",
    "DCO's Gyani": "Takes time to understand",
    "DCO's Influencer": "Office celeb — always posting stories, reels, and selfies.",
    "DCO's Style Icon": "The one who turns the office corridor into a runway.",
    "DCO's Scariest Manager": "A single \"Come to my cabin\" is enough to cause panic.",
    "DCO's Chill Manager": "Coolest boss ever — strict on deadlines, soft on people.",
    "DCO's Star (All-Rounder)": "Shines in every task.",
    "DCO's Chai Lover": "Life, work, and conversations - all powered by chai.",
    "DCO's Sabka Dost, Kaam Ke Time Ghost": "Social butterfly who disappears exactly when work starts.",
    "DCO's Phone Pe Hi Busy": "Perpetually on \"important calls\" that never seem to end.",
    "DCO's 2-Min Break = 2-Hour Walk": "Vanishes for \"just 2 mins\" and returns after sunset.",
    "DCO's Deadline Warrior": "Works best when the deadline was yesterday.",
    "DCO's Tech Guru": "The go-to person when nothing is working",
    "DCO's Fitness Freak": "Hits the gym even after 10-hour workdays.",
    "DCO's Drama Queen/King": "Turns every tiny issue into a full episode.",
    "DCO's Gumnaam": "Jo km bolte h",
    "DCO's Workholic": "DCO's Workholic",
    "DCO's Most Punctual": "DCO's Most Punctual",
    "DCO's Strongest Pillar": "DCO's Hero"
}

# Award options for each category
award_options = {
    "DCO's Bhukhad": ["Kunal Rajwani", "Sudhakar Kumar", "Romil Nagori", "Arihant Jain"],
    "DCO's Late Latif": ["Divyanshu Jain", "Kunal Rajwani", "Adish Jain", "Gargi paliwal"],
    "DCO's Bheja Fry": ["Aryan Jain", "Harshit Jain", "Adish Jain", "Priya Sharma"],
    "DCO's Chapad Chapad": ["Mahak Gandhi", "Megha Toshniwal", "Harshita Solanki", "Keerti Sharma"],
    "DCO's Goli Master": ["Divya Gupta", "Somil", "Mudit Jain", "Romil Nagori"],
    "DCO's Narad Muni": ["Sneha Mishra", "Deena Arora", "Naresh Sharma", "Keerti Sharma"],
    "DCO's Bindas Insaan": ["Somil", "Shefali Jain", "Ritika Agarwal", "Nirali Chhabra"],
    "DCO's Most Sanskari": ["Diksha Hirani", "Prachi Gupta", "Ayush Jain", "Nirali Chhabra"],
    "DCO's Kamchor": ["Sudhakar Kumar", "Virendra kumar sharma", "Adish Jain", "Arihant Jain"],
    "DCO's Chupa Rustom": ["Gargi Gupta", "Om Prakash", "Arun Maur", "Naresh Sharma"],
    "DCO's Ladaku": ["Kunal Rajwani", "Divyanshu Jain", "Romil Nagori", "Gargi paliwal"],
    "DCO's MF Husain": ["Somya Jain", "Shreyansh Jain", "Harshita Solanki", "Ananya Kayal"],
    "DCO's Dancer": ["Somil", "Rahul", "Harshita Solanki", "Ananya Kayal"],
    "DCO's Gyani": ["Hardik Lodha", "Divya Gupta", "Ananya Jain", "Tushar Singh Sisodiya"],
    "DCO's Influencer": ["Sanyam Saraf", "Mahak Gandhi", "Adish Jain", "Adish Jain"],
    "DCO's Style Icon": ["Shreyansh Jain", "Pranjul Saini", "Ananya Jain", "Nirali Chhabra"],
    "DCO's Scariest Manager": ["Shuchi Sethi", "Safal Sethi", "Gargi paliwal", "Romil Nagori"],
    "DCO's Chill Manager": ["Shefali Jain", "Dheera", "Mudit Jain", "Sourabh Chhipa"],
    "DCO's Star (All-Rounder)": ["Kashvi Katiyar", "Somya Jain", "Ananya Kayal", "Tushar Singh Sisodiya"],
    "DCO's Chai Lover": ["Safal Sethi", "Rajesh Meena", "Gargi paliwal", "Romil Nagori"],
    "DCO's Sabka Dost, Kaam Ke Time Ghost": ["Priyanshu", "Somil", "Ananya Jain", "Raghav Maheshwari"],
    "DCO's Phone Pe Hi Busy": ["Yash Dhadda", "Sourabh Chhipa", "Ananya Jain", "Romil Nagori"],
    "DCO's 2-Min Break = 2-Hour Walk": ["Khushboo Sangtani", "Deena Arora", "Adish Jain", "Keerti Sharma"],
    "DCO's Deadline Warrior": ["Sourabh Chhipa", "Shradha Sareen", "Yash Vijay", "Neha Jain"],
    "DCO's Tech Guru": ["Somya Jain", "Sanyam Saraf", "Yash Vijay", "Mudit Jain"],
    "DCO's Fitness Freak": ["Shreyansh Jain", "Virendra kumar sharma", "Aman Baid", "Sanyam Saraf"],
    "DCO's Drama Queen/King": ["Kajal", "Megha Toshniwal", "Ananya Kayal", "Arihant Jain"],
    "DCO's Gumnaam": ["Suresh Das Vaishnav", "Gunin Janyani", "Arun Maur", "Chanchal Maheshwari"],
    "DCO's Workholic": ["Yash Kumawat", "Ayushi Bagrecha", "Harshita Solanki", "Neha Jain"],
    "DCO's Most Punctual": ["Gargi Gupta", "Shresth Mittal", "Yash Vijay", "Mudit Jain"],
    "DCO's Strongest Pillar": ["Princy Dhadda", "Yash Dhadda", "Mudit Jain", "Arvind Dhadda"]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    password = request.args.get('password')
    if password != '95875001':
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>DCO Awards 2025 - Admin Access</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f0f8f0; }
                .card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 400px; margin: 0 auto; }
                .error { color: #e74c3c; margin: 20px 0; }
                input { padding: 10px; margin: 10px; width: 200px; border: 1px solid #ddd; border-radius: 5px; }
                button { padding: 10px 20px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }
                button:hover { background: #45a049; }
            </style>
        </head>
        <body>
            <div class="card">
                <h2>🔒 Admin Access Required</h2>
                <p>Please enter the admin password to access host controls.</p>
                <form method="get">
                    <input type="password" name="password" placeholder="Enter admin password" required>
                    <br>
                    <button type="submit">Access Host Controls</button>
                </form>
                <div class="error">Incorrect password. Please try again.</div>
                <p><a href="/">← Back to Home</a></p>
            </div>
        </body>
        </html>
        ''', 401
    return render_template('admin.html', awards=awards, award_options=award_options, award_intros=award_intros)

@app.route('/vote')
def vote():
    current_award = awards[question_index] if question_index < len(awards) else "No active poll"
    current_options = award_options.get(current_award, []) if question_index < len(awards) else []
    return render_template('vote.html', current_award=current_award, current_options=current_options)


@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    current_options = award_options.get(current_question, []) if current_question else []
    current_intro = award_intros.get(current_question, '') if current_question else ''
    # Create a clean votes object for display (without voter IDs)
    display_votes = {}
    for k, v in votes.items():
        # Skip if this is a voter ID (not a choice name)
        if k not in award_options.get(current_question, []):
            continue
        display_votes[k] = v
    emit('status_update', {
        'current_question': current_question,
        'current_options': current_options,
        'current_intro': current_intro,
        'question_index': question_index,
        'is_polling_active': is_polling_active,
        'total_votes': total_votes,
        'votes': display_votes
    })

@socketio.on('start_poll')
def handle_start_poll(data):
    global current_question, question_index, votes, is_polling_active, total_votes
    
    question_index = data.get('question_index', 0)
    if 0 <= question_index < len(awards):
        current_question = awards[question_index]
        current_options = award_options.get(current_question, [])
        current_intro = award_intros.get(current_question, '')
        votes = {}
        is_polling_active = True
        total_votes = 0
        
        emit('poll_started', {
            'question': current_question,
            'options': current_options,
            'intro': current_intro,
            'question_index': question_index
        }, broadcast=True)
        
        print(f'Poll started: {current_question}')

@socketio.on('end_poll')
def handle_end_poll():
    global is_polling_active
    is_polling_active = False
    
    # Create a clean votes object for display (without voter IDs)
    display_votes = {}
    for k, v in votes.items():
        # Skip if this is a voter ID (not a choice name)
        if k not in award_options.get(current_question, []):
            continue
        display_votes[k] = v
    
    emit('poll_ended', {
        'votes': display_votes,
        'total_votes': total_votes
    }, broadcast=True)
    
    print('Poll ended')

@socketio.on('next_question')
def handle_next_question():
    global question_index, current_question, votes, is_polling_active, total_votes
    
    question_index += 1
    if question_index < len(awards):
        current_question = awards[question_index]
        current_options = award_options.get(current_question, [])
        current_intro = award_intros.get(current_question, '')
        votes = {}
        is_polling_active = True
        total_votes = 0
        
        emit('question_changed', {
            'question': current_question,
            'options': current_options,
            'intro': current_intro,
            'question_index': question_index
        }, broadcast=True)
        
        print(f'Next question: {current_question}')
    else:
        emit('all_questions_complete', broadcast=True)
        print('All questions completed')

@socketio.on('vote')
def handle_vote(data):
    global votes, total_votes
    
    if not is_polling_active:
        return
    
    voter_id = request.sid
    choice = data.get('choice')
    
    if choice:
        # Remove previous vote if exists
        if voter_id in votes:
            old_choice = votes[voter_id]
            if old_choice in votes:
                votes[old_choice] = votes.get(old_choice, 1) - 1
                if votes[old_choice] <= 0:
                    del votes[old_choice]
                total_votes -= 1
        
        # Add new vote
        votes[voter_id] = choice
        votes[choice] = votes.get(choice, 0) + 1
        total_votes += 1
        
        # Create a clean votes object for display (without voter IDs)
        # Voter IDs are the socket IDs, so we need to filter them out
        # Keep only the vote counts for each choice
        display_votes = {}
        for k, v in votes.items():
            # Skip if this is a voter ID (not a choice name)
            if k not in award_options.get(current_question, []):
                continue
            display_votes[k] = v
        
        print(f'Vote received: {choice}')
        print(f'Votes object: {votes}')
        print(f'Display votes: {display_votes}')
        print(f'Total votes: {total_votes}')
        
        emit('vote_update', {
            'votes': display_votes,
            'total_votes': total_votes,
            'voter_choice': choice
        }, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    global votes, total_votes
    
    voter_id = request.sid
    if voter_id in votes:
        choice = votes[voter_id]
        if choice in votes:
            votes[choice] = votes.get(choice, 1) - 1
            if votes[choice] <= 0:
                del votes[choice]
        del votes[voter_id]
        total_votes = max(0, total_votes - 1)
        
        # Create a clean votes object for display (without voter IDs)
        display_votes = {}
        for k, v in votes.items():
            # Skip if this is a voter ID (not a choice name)
            if k not in award_options.get(current_question, []):
                continue
            display_votes[k] = v
        
        emit('vote_update', {
            'votes': display_votes,
            'total_votes': total_votes
        }, broadcast=True)
    
    print(f'Client disconnected: {request.sid}')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)

