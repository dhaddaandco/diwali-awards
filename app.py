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

# 30 Fun Award Categories
awards = [
    "Most Likely to Survive a Zombie Apocalypse",
    "Best Coffee Addiction",
    "Most Creative Excuse for Being Late",
    "Best Zoom Background",
    "Most Likely to Win a Karaoke Contest",
    "Best Desk Decoration",
    "Most Likely to Bring Snacks to Every Meeting",
    "Best Email Signature",
    "Most Likely to Remember Everyone's Birthday",
    "Best PowerPoint Animation Skills",
    "Most Likely to Have a Pet at Work",
    "Best Meme Creator",
    "Most Likely to Win a Dance-Off",
    "Best Office Plant Parent",
    "Most Likely to Have a Secret Talent",
    "Best Meeting Icebreaker",
    "Most Likely to Win a Costume Contest",
    "Best Slack Reaction Game",
    "Most Likely to Have a Side Hustle",
    "Best Office Joke Teller",
    "Most Likely to Win a Trivia Night",
    "Best Work-From-Home Setup",
    "Most Likely to Have a Collection",
    "Best Team Spirit",
    "Most Likely to Win a Cooking Contest",
    "Best Office Playlist Curator",
    "Most Likely to Have a Catchphrase",
    "Best Problem Solver",
    "Most Likely to Win a Scavenger Hunt",
    "Best Team Player"
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html', awards=awards)

@app.route('/vote')
def vote():
    return render_template('vote.html')

@app.route('/results')
def results():
    return render_template('results.html')

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('status_update', {
        'current_question': current_question,
        'question_index': question_index,
        'is_polling_active': is_polling_active,
        'total_votes': total_votes,
        'votes': votes
    })

@socketio.on('start_poll')
def handle_start_poll(data):
    global current_question, question_index, votes, is_polling_active, total_votes
    
    question_index = data.get('question_index', 0)
    if 0 <= question_index < len(awards):
        current_question = awards[question_index]
        votes = {}
        is_polling_active = True
        total_votes = 0
        
        emit('poll_started', {
            'question': current_question,
            'question_index': question_index
        }, broadcast=True)
        
        print(f'Poll started: {current_question}')

@socketio.on('end_poll')
def handle_end_poll():
    global is_polling_active
    is_polling_active = False
    
    emit('poll_ended', {
        'votes': votes,
        'total_votes': total_votes
    }, broadcast=True)
    
    print('Poll ended')

@socketio.on('next_question')
def handle_next_question():
    global question_index, current_question, votes, is_polling_active, total_votes
    
    question_index += 1
    if question_index < len(awards):
        current_question = awards[question_index]
        votes = {}
        is_polling_active = True
        total_votes = 0
        
        emit('question_changed', {
            'question': current_question,
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
        
        # Add new vote
        votes[voter_id] = choice
        votes[choice] = votes.get(choice, 0) + 1
        total_votes += 1
        
        emit('vote_update', {
            'votes': votes,
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
        
        emit('vote_update', {
            'votes': votes,
            'total_votes': total_votes
        }, broadcast=True)
    
    print(f'Client disconnected: {request.sid}')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)

