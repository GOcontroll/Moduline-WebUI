from microdot import Microdot, Response, redirect, send_file
from microdot.session import Session, with_session
from functools import wraps
import random
import string
import os
import json

BASE_TEMPLATE = '''<!doctype html>
<html>
  <head>
    <title>GOcontroll</title>
    <meta charset="UTF-8">
  </head>
  <body>
    <h1>GOcontroll login</h1>
    {content}
  </body>
</html>'''

LOGGED_OUT = '''<p>You are not logged in.</p>
<form method="POST">
  <p>
    Passkey:
    <input name="passkey" autofocus />
  </p>
  <input type="submit" value="Submit" />
</form>'''

FAILED_LOGIN = '''<p>You are not logged in.</p>
<form method="POST">
  <p>
    Passkey:
    <input name="passkey" autofocus />
  </p>
  <input type="submit" value="Submit" />
  <p>Incorrect passkey entered</p>
</form>'''

NO_LOGIN = '''<p>You have tried to log in too many times and can't try again.</p>
'''

def authenticate_token(token:str) -> bool:
	try:
		tokens.index(token)
		return True
	except ValueError:
		return False
	
def register_token(token:str):
	tokens.append(token)

def remove_token(token:str):
	try:
		tokens.remove(token)
	except ValueError:
		pass

def auth(func):
	@wraps(func)
	async def wrapper(req, session, *args, **kwargs):
		if not authenticate_token(session.get('token')):
			return redirect('/')
		return await func(req, session, *args, **kwargs)
	return wrapper

app = Microdot()
Session(app, secret_key='top-secret')
Response.default_content_type = 'text/html'

@app.get('/')
@app.post('/')
@with_session
async def index(req, session):
	token = session.get('token')
	if req.method == 'POST':
		passkey = req.form.get('passkey')
		if passkey == "test":
			token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
			session['token'] = token
			register_token(token)
			session.save()
			return redirect('/static/home.html')
		else:
			return BASE_TEMPLATE.format(content=FAILED_LOGIN)
	if token is None or not authenticate_token(token):
		return BASE_TEMPLATE.format(content=LOGGED_OUT)
	elif authenticate_token(token):
		return redirect('/static/home.html')


@app.post('/logout')
@with_session
async def logout(req, session):
	remove_token(session.get('token'))
	session.delete()
	return redirect('/')

@app.route('/static/<path:path>')
@with_session
@auth
async def static(request, session, path):
	if '..' in path:
		return 'Not allowed', 404
	return send_file('static/' + path)

@app.route('/style/<path:path>')
async def style(request, path):
	if '..' in path:
		return 'Not allowed', 404
	return send_file('style/' + path)

@app.route('/js/<path:path>')
async def js(request, path):
	if '..' in path:
		return 'Not allowed', 404
	return send_file('js/' + path)

@app.get('/favicon.ico')
async def favicon(request):
	return send_file('favicon.ico')

@app.get('/api/get_sim_ver')
@with_session
@auth
async def sim_ver(request, session):
	try:
		with open('/usr/simulink/CHANGELOG.md', 'r') as changelog:
			head = changelog.readline()
		return json.dumps(head.split(' ')[1])
	except:
		return json.dumps("No changelog found")

@app.get('/api/download_a2l')
@with_session
@auth
async def a2l_down(request,session):
	return send_file('/usr/simulink/GOcontroll_Linux.a2l')

@app.get('/api/get_wifi')
@with_session
@auth
async def get_wifi(request, session):
	return json.dumps(not os.path.isfile('/etc/modprobe.d/brcmfmac.conf'))

if __name__ == '__main__':
	tokens = []
	app.run()
