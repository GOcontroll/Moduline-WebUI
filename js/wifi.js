async function set_wifi() {
	//get what the next state of wifi should be
	let set_state = {};
	const cb = document.getElementById("wifi");
	set_state.new_state = cb.checked;
	//try to make it a reality
	try{
		const resp = await post_json("/api/set_wifi", set_state);
		if (resp.err != undefined) {
			//server failed to toggle wifi
			cb.checked = !cb.checked;
			alert("Could not toggle wifi:\n"+resp.err);
		}
	} catch(err) {
		alert("Could not toggle wifi:\n" + err);
		cb.checked = !cb.checked;
	}
}

async function set_ap_ssid() {
	const input = document.getElementById("ap_ssid");
	const result = document.getElementById("set_ap_ssid_result");
	const ssid = input.value;
	if (ssid.length > 0){
		try {
			await post_json("/api/set_ap_ssid", pass);
			result.innerText = "Success!"
			input.value = "";
		} catch (err) {
			alert("could not set AP ssid:\n" +err);
		}
	} else {
		result.innerText = "SSID cannot be empty"
	}
}

async function set_ap_pass() {
	const input = document.getElementById("ap_pass");
	const result = document.getElementById("set_ap_pass_result");
	const pass = input.value;
	// let pass = $("#ap_pass").val();
	if (pass.length > 0){
		try {
			await post_json("/api/set_ap_pass", pass);
			result.innerText = "Success!"
			input.value = "";
		} catch (err) {
			alert("could not set AP password:\n" +err);
		}
	} else {
		result.innerText = "Password cannot be empty"
	}
}

async function toggle_ap_pass() {
	const input = document.getElementById("ap_pass");
	if (input.getAttribute("type") === "password") {
		input.setAttribute("type", "text")
	} else if (input.getAttribute("type") === "text") {
		input.setAttribute("type", "password")
	}
}

document.addEventListener('DOMContentLoaded', async function() {
	const wifi_request = await (await fetch('/api/get_wifi')).json();
	document.getElementById("wifi").checked = wifi_request;
}, false);