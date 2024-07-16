document.addEventListener('DOMContentLoaded', async function() {
	const wwan_request = await (await fetch('/api/get_wwan')).json();
	document.getElementById("wwan").checked = wwan_request.state;
}, false);

async function set_wwan() {
	//get what the next state of wwan should be
	let set_state = {};
	const cb = document.getElementById("wwan");
	set_state.new_state = cb.checked;
	//try to make it a reality
	try{
		const resp = await post_json("/api/set_wwan", set_state);
		if (resp.err != undefined) {
			//server failed to toggle wwan
			cb.checked = !cb.checked;
			alert("Could not toggle wwan:\n"+resp.err);
		}
	} catch(err) {
		alert("Could not toggle wwan:\n" + err);
		cb.checked = !cb.checked;
	}
}