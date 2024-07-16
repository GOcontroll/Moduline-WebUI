async function set_wwan() {
	//get what the next state of wwan should be
	let set_state = {};
	const cb = document.getElementById("wwan");
    //current state of checked is after it was clicked, so the state it needs to become
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

document.addEventListener('DOMContentLoaded', async function() {
    try {
	    const wwan_request = await (await fetch('/api/get_wwan')).json();
        document.getElementById("wwan").checked = wwan_request.state;
        if (wwan_request.state) {
            const wwan_stats_request = await (await fetch('/api/get_wwan_stats')).json();
            if (wwan_stats_request.err) {
                console.log(wwan_stats_request.err);
                return;
            }
            document.getElementById("imei").innerText = wwan_stats_request.imei;
            document.getElementById("operator").innerText = wwan_stats_request.operator;
            document.getElementById("model").innerText = wwan_stats_request.model;
            document.getElementById("signal").innerText = wwan_stats_request.signal;
        }
    } catch(err) {
        console.log(err);
        return;
    }
	
}, false);
