async function post_json(url, data) {
	return (await fetch(url, 
		{
			method: 'POST', 
			body: JSON.stringify(data),
			headers: {"Content-type": "application/json; charset=UTF-8"}
		})).json()
}

async function set_wifi() {
	//get what the next state of wifi should be
	let set_state;
	if (!$("#wifi").prop("checked")) { //why does this work with a not?
		set_state = false;
	} else {
		set_state = true;
	}
	//try to make it a reality
	try{
		const resp = await post_json("/api/set_wifi", set_state);
		if (resp != set_state) {
			//server failed to toggle wifi
			$('#wifi').prop("checked",resp);
			alert("Could not toggle wifi");
		}
	} catch(err) {
		alert("Could not toggle wifi:\n" + err);
		$('#wifi').prop("checked",!set_state);
	}
}

async function set_ap_pass() {
	let pass = $("#ap_pass").val();
	if (pass.length > 0){
		try {
			await post_json("/api/set_ap_pass", pass);
			$("#set_ap_pass_result").html("Success!")
			$("#ap_pass").val("");
		} catch (err) {
			alert("could not set AP password:\n" +err);
		}
	} else {
		$("#set_ap_pass_result").html("password cannot be empty")
	}
}

document.addEventListener('DOMContentLoaded', async function() {
    const simulink_request = await fetch('/api/get_sim_ver');
	$('#simulink_version').html(await simulink_request.json());

	const wifi_request = await (await fetch('/api/get_wifi')).json();
	$('#wifi').prop("checked",wifi_request);
}, false);