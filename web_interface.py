"""
Daemon Web Interface - Flask-based interface for operatives
This provides the user-facing interface for the daemon system.
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import secrets
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from daemon_core import DaemonCore
from dotenv import load_dotenv
import fade
# Load environment variables
load_dotenv('.env')
banner = r"""
###########+-..           .......++--++#++...      .                   ..-.--....   ... .         ..
##########+++--..           .....--+.#-+++.+..                   ..-.....-.-.....  .......          
####++++-----....            ...-.-+-+++#--...             .     ..--++-+.+--....     ......        
###++##########..             ....--+.#-+...             . . . .....---+-#-+-.........              
####+###+..####..               ...----... .             . .  . . ..-----+--.-........-.............
####+###++-####..   .#######+.     ..+#####-.  ...+###############....+--+#######......+#########-.-
##+-+###+--####..   .#########.  ..-#########. . .+################. ...####++####-....+###+--####.-
+++-+###+..####..     ....+###. ...####..-###.   .+###...###+  ####.   .####..-###-....+###-..####.-
....-###- .####.. . +#########.  ..####. -###.    +###...###+ .####.   .####. -###-.-..-###-..####..
....-###-..####.....####..####. .. ####-.+###. . .+###...###+ .####.   .####. -###-.--.+###-..####.-
....-###-..####.---.###+..+###.. ..##########.....+###. .###+ .####.   .####. -###-.--.+###---####.-
.  .-###-..####.  ..###+ .####.  ..####.... .  .. +###  .###+ .####.   .####..-###-....+###-..####.-
....+###-..####.   .###+..####. ...####-------... +###  .###+ .####.  ..####.--###+-++-+###---####.+
. ..+###-..####.. ..###+..####. .-.####..-###-... +###  .###- .####. . .####..-###+++-.+###-..####..
. ..+#########+.....##########.....-########+.-.. ####  .###- .####.....-#########.--+.+###-..####..
.----+++++++-..-++++--++++++++..-++-.-+##+-...-.. .++-  .+++.  -+++.-+-.-.-++#++---+###+++++++++++-+
..-.-.-.-...   ........    ...    ...           .                .. -. -.--..-.  ... ..------+----+-
"""
print (fade.purplepink(banner))
app = Flask(__name__)
# Use secret key from .env or generate a random one
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
CORS(app)

# Initialize daemon core
daemon = DaemonCore()

# Store sessions securely
SESSION_DIR = Path("./daemon_data/sessions")
SESSION_DIR.mkdir(exist_ok=True, parents=True)


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate_operative(operative_id: str, password_hash: str) -> bool:
    """Authenticate an operative"""
    auth_file = Path("./daemon_data/auth.json")
    if not auth_file.exists():
        return False
    
    with open(auth_file, 'r') as f:
        auth_data = json.load(f)
    
    return auth_data.get(operative_id) == password_hash


@app.route('/')
def index():
    """Main landing page"""
    if 'operative_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/recruit', methods=['GET', 'POST'])
def recruit():
    """Recruitment page for new operatives"""
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        skills = data.get('skills', [])
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Create operative
        operative_id = daemon.recruit_operative(username, skills)
        
        # Store auth credentials
        password_hash = hash_password(password)
        auth_file = Path("./daemon_data/auth.json")
        
        auth_data = {}
        if auth_file.exists():
            with open(auth_file, 'r') as f:
                auth_data = json.load(f)
        
        auth_data[operative_id] = password_hash
        
        with open(auth_file, 'w') as f:
            json.dump(auth_data, f)
        
        operative = daemon.operatives[operative_id]
        
        return jsonify({
            'success': True,
            'operative_id': operative_id,
            'darknet_name': operative.darknet_name,
            'message': 'Welcome to the network. Your identity has been encoded.'
        })
    
    return render_template('recruit.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for existing operatives"""
    if request.method == 'POST':
        data = request.json
        operative_id = data.get('operative_id')
        password = data.get('password')
        
        password_hash = hash_password(password)
        
        if authenticate_operative(operative_id, password_hash):
            session['operative_id'] = operative_id
            return jsonify({'success': True, 'redirect': url_for('dashboard')})
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout current operative"""
    session.pop('operative_id', None)
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    """Main dashboard for operatives"""
    if 'operative_id' not in session:
        return redirect(url_for('login'))
    
    operative_id = session['operative_id']
    operative = daemon.operatives.get(operative_id)
    
    if not operative:
        return redirect(url_for('logout'))
    
    return render_template('dashboard.html', operative=operative)


@app.route('/api/operative/profile')
def get_profile():
    """Get operative profile"""
    if 'operative_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    operative_id = session['operative_id']
    operative = daemon.operatives.get(operative_id)
    
    if not operative:
        return jsonify({'error': 'Operative not found'}), 404
    
    from dataclasses import asdict
    return jsonify(asdict(operative))


@app.route('/api/quests')
def get_quests():
    """Get available and assigned quests"""
    if 'operative_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    operative_id = session['operative_id']
    operative = daemon.operatives.get(operative_id)
    
    if not operative:
        return jsonify({'error': 'Operative not found'}), 404
    
    # Get available quests
    available_quests = []
    active_quests = []
    completed_quests = []
    
    from dataclasses import asdict
    
    for quest in daemon.quests.values():
        quest_dict = asdict(quest)
        
        if quest.status == 'available' and quest.requirements.get('min_rank', 0) <= operative.rank:
            available_quests.append(quest_dict)
        elif quest.status == 'active' and quest.assigned_to == operative_id:
            active_quests.append(quest_dict)
        elif quest.status == 'completed' and quest.quest_id in operative.completed_quests:
            completed_quests.append(quest_dict)
    
    return jsonify({
        'available': available_quests,
        'active': active_quests,
        'completed': completed_quests
    })


@app.route('/api/quest/<quest_id>/accept', methods=['POST'])
def accept_quest(quest_id):
    """Accept a quest"""
    if 'operative_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    operative_id = session['operative_id']
    
    if daemon.assign_quest(quest_id, operative_id):
        return jsonify({'success': True, 'message': 'Quest accepted'})
    else:
        return jsonify({'error': 'Could not accept quest'}), 400


@app.route('/api/quest/<quest_id>/complete', methods=['POST'])
def complete_quest(quest_id):
    """Complete a quest"""
    if 'operative_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    operative_id = session['operative_id']
    
    if daemon.complete_quest(quest_id, operative_id):
        return jsonify({'success': True, 'message': 'Quest completed! Rewards granted.'})
    else:
        return jsonify({'error': 'Could not complete quest'}), 400


@app.route('/api/network/status')
def network_status():
    """Get overall network status"""
    return jsonify({
        'total_operatives': len(daemon.operatives),
        'active_operatives': sum(1 for op in daemon.operatives.values() if op.active),
        'total_quests': len(daemon.quests),
        'completed_quests': sum(1 for q in daemon.quests.values() if q.status == 'completed'),
        'active_triggers': sum(1 for t in daemon.triggers.values() if t.active),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/leaderboard')
def leaderboard():
    """Get operative leaderboard"""
    from dataclasses import asdict
    
    operatives = sorted(
        daemon.operatives.values(),
        key=lambda op: (op.rank, op.reputation),
        reverse=True
    )
    
    return jsonify([
        {
            'darknet_name': op.darknet_name,
            'rank': op.rank,
            'reputation': op.reputation,
            'completed_quests': len(op.completed_quests)
        }
        for op in operatives[:10]
    ])


@app.route('/triggers')
def triggers_page():
    """Trigger management page"""
    if 'operative_id' not in session:
        return redirect(url_for('login'))
    
    operative_id = session['operative_id']
    operative = daemon.operatives.get(operative_id)
    
    if not operative or operative.rank < 3:
        return "Access denied. Rank 3+ required for trigger management.", 403
    
    return render_template('triggers.html')


@app.route('/api/trigger/create', methods=['POST'])
def create_trigger():
    """Create a new trigger from natural language description"""
    if 'operative_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    operative_id = session['operative_id']
    operative = daemon.operatives.get(operative_id)
    
    if not operative or operative.rank < 3:
        return jsonify({'error': 'Insufficient rank. Rank 3+ required.'}), 403
    
    data = request.json
    description = data.get('description')
    
    if not description:
        return jsonify({'error': 'Description required'}), 400
    
    import asyncio
    
    # Run async trigger creation
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        trigger_id = loop.run_until_complete(
            daemon.create_trigger_from_natural_language(description)
        )
        loop.close()
        
        if trigger_id:
            return jsonify({
                'success': True,
                'trigger_id': trigger_id,
                'status': 'active',
                'message': 'Trigger has been analyzed by AI and activated successfully.'
            })
        else:
            return jsonify({
                'error': 'Failed to create trigger. It may have been rejected for safety reasons.'
            }), 400
    except Exception as e:
        return jsonify({'error': f'Error creating trigger: {str(e)}'}), 500


@app.route('/api/triggers')
def get_triggers():
    """Get all triggers"""
    if 'operative_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    from dataclasses import asdict
    
    triggers = [asdict(t) for t in daemon.triggers.values()]
    
    return jsonify({'triggers': triggers})


@app.route('/api/quest/generate', methods=['POST'])
def generate_quest():
    """Generate a new quest using AI"""
    if 'operative_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    operative_id = session['operative_id']
    operative = daemon.operatives.get(operative_id)
    
    if not operative or operative.rank < 3:
        return jsonify({'error': 'Insufficient rank. Rank 3+ required.'}), 403
    
    data = request.json
    difficulty = data.get('difficulty', 2)
    
    import asyncio
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        quest_id = loop.run_until_complete(
            daemon.generate_quest_with_ai(difficulty)
        )
        loop.close()
        
        if quest_id:
            return jsonify({
                'success': True,
                'quest_id': quest_id,
                'message': 'Quest generated by AI successfully.'
            })
        else:
            return jsonify({'error': 'Failed to generate quest'}), 400
    except Exception as e:
        return jsonify({'error': f'Error generating quest: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
