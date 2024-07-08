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
	let set_state = {};
	if (!$("#wifi").prop("checked")) { //why does this work with a not?
		set_state.new_state = false;
	} else {
		set_state.new_state = true;
	}
	//try to make it a reality
	try{
		const resp = await post_json("/api/set_wifi", set_state);
		if (resp.err != undefined) {
			//server failed to toggle wifi
			$('#wifi').prop("checked",!set_state.new_state);
			alert("Could not toggle wifi:\n"+resp.err);
		}
	} catch(err) {
		alert("Could not toggle wifi:\n" + err);
		$('#wifi').prop("checked",!set_state.new_state);
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
	const sn_request = fetch("/api/get_serial_number");
	const software_request = fetch('/api/get_software');
	const hardware_request = fetch("/api/get_hardware");
    const simulink_request = fetch('/api/get_sim_ver');
	res = await (await sn_request).json();
	if (res.err) {
		$("#serial_number").html(res.err);
	} else {
		$("#serial_number").html(res.sn);
	}
	res = await (await software_request).json();
	if (res.err) {
		$("#controller_software").html(res.err);
	} else {
		$("#controller_software").html(res.version);
	}
	res = await (await hardware_request).json();
	if (res.err) {
		$("#controller_hardware").html(res.err);
	} else {
		$("#controller_hardware").html(res.hardware);
	}
	res = await (await simulink_request).json();
	if (res.err) {
		$('#simulink_version').html(res.err);
	} else {
		$('#simulink_version').html(res.version);
	}

	const wifi_request = await (await fetch('/api/get_wifi')).json();
	$('#wifi').prop("checked",wifi_request);
}, false);