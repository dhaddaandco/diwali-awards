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
    return render_template('admin.html', awards=awards, award_options=award_options)

@app.route('/vote')
def vote():
    current_award = awards[question_index] if question_index < len(awards) else "No active poll"
    current_options = award_options.get(current_award, []) if question_index < len(awards) else []
    return render_template('vote.html', current_award=current_award, current_options=current_options)


@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    current_options = award_options.get(current_question, []) if current_question else []
    # Create a clean votes object for display (without voter IDs)
    display_votes = {k: v for k, v in votes.items() if not k.startswith('socket_')}
    emit('status_update', {
        'current_question': current_question,
        'current_options': current_options,
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
        votes = {}
        is_polling_active = True
        total_votes = 0
        
        emit('poll_started', {
            'question': current_question,
            'options': current_options,
            'question_index': question_index
        }, broadcast=True)
        
        print(f'Poll started: {current_question}')

@socketio.on('end_poll')
def handle_end_poll():
    global is_polling_active
    is_polling_active = False
    
    # Create a clean votes object for display (without voter IDs)
    display_votes = {k: v for k, v in votes.items() if not k.startswith('socket_')}
    
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
        votes = {}
        is_polling_active = True
        total_votes = 0
        
        emit('question_changed', {
            'question': current_question,
            'options': current_options,
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
        display_votes = {k: v for k, v in votes.items() if not k.startswith('socket_') and k != voter_id}
        
        emit('vote_update', {
            'votes': display_votes,
            'total_votes': total_votes,
            'voter_choice': choice
        }, broadcast=True)
        
        print(f'Vote received: {choice}')

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
        display_votes = {k: v for k, v in votes.items() if not k.startswith('socket_')}
        
        emit('vote_update', {
            'votes': display_votes,
            'total_votes': total_votes
        }, broadcast=True)
    
    print(f'Client disconnected: {request.sid}')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)

