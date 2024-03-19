from flask import Flask, session, render_template
import os
from flask_session import Session
from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
import atexit

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Set Flask session options
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

logs = []

def run_script():
    # result = subprocess.run(['python', 'scripts/run_lunchbot.py', '>', '/tmp/lunchbot_run_logs.txt'], capture_output=True, shell=True)
    # os.system('python scripts/run_lunchbot.py > /tmp/lunchbot_run_logs.txt')
    # change to directory one level up, then run setup.sh, and then the run_lunchbot.py script
    os.system('bash -c "source setup.sh && python scripts/run_lunchbot.py &>> /tmp/lunchbot_run_logs.txt"')
    # logs.append(result.stdout)
    with open("/tmp/lunchbot_run_logs.txt") as f:
        logs.append(f.read())

scheduler = BackgroundScheduler()
# scheduler.add_job(func=run_script, trigger="interval", minutes=5)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

@app.route('/run-script', methods=['POST'])
def run_script_route():
    run_script()
    return ('', 204)

@app.route('/')
def home():
    if 'counter' not in session:
        session['counter'] = 0
    else:
        session['counter'] += 1
    return render_template('index.html', counter=session['counter'], logs=logs)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=777)
    # run_script()