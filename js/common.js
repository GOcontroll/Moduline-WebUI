async function post_json(url, data) {
	return (await fetch(url, 
		{
			method: 'POST', 
			body: JSON.stringify(data),
			headers: {"Content-type": "application/json; charset=UTF-8"}
		})).json()
}