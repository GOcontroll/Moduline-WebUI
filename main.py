from microdot import Microdot, Response, Request, redirect, send_file
from microdot.session import Session, with_session
from functools import wraps
import random
import string
import os
import json
import wifi
import controller
import ethernet

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
    <input type="password" name="passkey" autofocus />
  </p>
  <input type="submit" value="Submit" />
</form>'''

FAILED_LOGIN = '''<p>You are not logged in.</p>
<form method="POST">
  <p>
    Passkey:
    <input type="password" name="passkey" autofocus />
  </p>
  <input type="submit" value="Submit" />
  <p>Incorrect passkey entered</p>
</form>'''

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
	async def wrapper(req: Request, session: Session, *args, **kwargs):
		if not authenticate_token(session.get('token')):
			return redirect('/')
		return await func(req, session, *args, **kwargs)
	return wrapper

app = Microdot()
Session(app, secret_key=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))) #generate new session key when the server is restarted
Response.default_content_type = 'text/html'

#########################################################################################################
#routes

#login

@app.get('/')
@app.post('/')
@with_session
async def index(req: Request, session: Session):
	token = session.get('token')
	if req.method == 'POST':
		passkey = req.form.get('passkey')
		if passkey == "test":
			token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10)) #generate new token for every new authorized session
			session['token'] = token
			register_token(token)
			session.save()
			return redirect('/static/home.html')
		else:
			return json.dumps(False)
	if token is None or not authenticate_token(token):
		return send_file('login.html')
	elif authenticate_token(token):
		return redirect('/static/home.html')


@app.post('/logout')
@with_session
async def logout(req: Request, session: Session):
	remove_token(session.get('token'))
	session.delete()
	return redirect('/')

#########################################################################################################

#file hosting

@app.route('/static/<path:path>')
@with_session
@auth
async def static(req: Request, session: Session, path: str):
	if '..' in path:
		return 'Not allowed', 404
	return send_file('static/' + path)

@app.route('/style/<path:path>')
async def style(req: Request, path):
	if '..' in path:
		return 'Not allowed', 404
	return send_file('style/' + path)

@app.route('/js/<path:path>')
async def js(request: Request, path):
	if '..' in path:
		return 'Not allowed', 404
	return send_file('js/' + path)

@app.get('/favicon.ico')
async def favicon(request: Request):
	return send_file('favicon.ico')

#########################################################################################################

#api

#simulink

@app.get('/api/get_sim_ver')
@with_session
@auth
async def sim_ver(req: Request, session: Session):
	return json.dumps(controller.get_sim_ver())
	
@app.get('/api/download_a2l')
@with_session
@auth
async def a2l_down(req: Request, session: Session):
	return send_file('/usr/simulink/GOcontroll_Linux.a2l')

#wifi

@app.get('/api/get_wifi')
@with_session
@auth
async def get_wifi(req: Request, session: Session):
	return json.dumps(not os.path.isfile('/etc/modprobe.d/brcmfmac.conf'))



@app.post('/api/set_wifi')
@with_session
@auth
async def set_wifi(req: Request, session: Session):
	"""Set the wifi state, request contains a json boolean value\n
	Returns the state of wifi after this function is finished"""
	new_state: bool = req.json
	if set_wifi(new_state):
		return json.dumps(new_state)
	else:
		return not json.dumps(new_state)
	
@app.post('/api/set_ap_pass')
@with_session
@auth
async def set_ap_pass(req: Request, session: Session):
	new_password: str = req.json
	wifi.set_ap_password(new_password)
	wifi.reload_ap()
	return Response("\"\"")

@app.post('/api/set_ap_ssid')
@with_session
@auth
async def set_ap_ssid(req: Request, session: Session):
	new_ssid: str = req.form.get('ssid')
	wifi.set_ap_ssid(new_ssid)
	wifi.reload_ap()
	return Response("\"\"")

#services

@app.get('/api/get_service')
@with_session
@auth
async def get_service(req: Request, session: Session):
	service: str = req.json
	return json.dumps(controller.get_service(service))

@app.post("/api/set_service")
@with_session
@auth
async def set_service(req: Request, session: Session):
	data = req.json
	new_state: bool = data["new_state"]
	service: str = data["service"]
	controller.set_service(service, new_state)
	return json.dumps(new_state)

#########################################################################################################

if __name__ == '__main__':
	tokens = []
	app.run()
