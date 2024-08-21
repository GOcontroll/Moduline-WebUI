async function set_wifi() {
	//get what the next state of wifi should be
	let set_state = {};
	const cb = document.getElementById("wifi");
	//current state of checked is after it was clicked, so the state it needs to become
	set_state.new_state = cb.checked;
	//warn user about possibility of terminating their connection
	if (!cb.checked) {
		if (!confirm("Turning off Wi-Fi could break your current connection to the server.")) {
			cb.checked = true;
			return;
		}
	}
	//try to make it a reality
	try {
		const resp = await post_json("/api/set_wifi", set_state);
		if (resp.err != undefined) {
			//server failed to toggle wifi
			cb.checked = !cb.checked;
			alert("Could not toggle wifi:\n" + resp.err);
		}
	} catch (err) {
		alert("Could not toggle wifi:\n" + err);
		cb.checked = !cb.checked;
	}
}

async function set_ap_ssid() {
	const input = document.getElementById("ap_ssid");
	const result = document.getElementById("set_ap_ssid_result");
	const ssid = input.value;
	if (ssid.length > 0) {
		try {
			const response = await post_json("/api/set_ap_ssid", ssid);
			if (response.err) {
				result.innerText = "Error: " + response.err;
				return;
			}
			result.innerText = "Success!";
			input.value = "";
		} catch (err) {
			result.innerText = "could not set AP ssid, invalid response";
			console.log("could not set AP ssid:\n" + err);
		}
	} else {
		result.innerText = "SSID cannot be empty"
	}
}

async function set_ap_pass() {
	const input = document.getElementById("ap_pass");
	const result = document.getElementById("set_ap_pass_result");
	const pass = input.value;
	if (pass.length > 7) {//if the password is shorter than 8 characters nmcli con mod will fail
		try {
			const response = await post_json("/api/set_ap_pass", pass);
			if (response.err) {
				result.innerText = "Error: " + response.err;
				return;
			}
			result.innerText = "Success!"
			input.value = "";
		} catch (err) {
			alert("could not set AP password:\n" + err);
		}
	} else if (pass.length == 0) {
		result.innerText = "Password cannot be empty"
	} else {
		result.innerText = "Password must be at least 8 characters long"
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

document.addEventListener('DOMContentLoaded', async function () {
	const wifi_request = await (await fetch('/api/get_wifi')).json();
	document.getElementById("wifi").checked = wifi_request.state;
}, false);
