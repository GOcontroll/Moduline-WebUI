document.addEventListener('DOMContentLoaded', async function() {
	const sn_request = fetch("/api/get_serial_number");
	const software_request = fetch('/api/get_software');
	const hardware_request = fetch("/api/get_hardware");
    const simulink_request = fetch('/api/get_sim_ver');
	var res = await (await sn_request).json();
	if (res.err) {
		document.getElementById("serial_number").innerText = "No controller serial number found";
        console.log(res.err);
	} else {
		document.getElementById("serial_number").innerText = res.sn;
	}
	res = await (await software_request).json();
	if (res.err) {
		document.getElementById("controller_software").innerText = "No controller software version found";
        console.log(res.err);
	} else {
		document.getElementById("controller_software").innerText = res.version;
	}
	res = await (await hardware_request).json();
	if (res.err) {
		document.getElementById("controller_hardware").innerText = "No controller hardware info found";
        console.log(res.err);
	} else {
		document.getElementById("controller_hardware").innerText = res.hardware;
	}
	res = await (await simulink_request).json();
	if (res.err) {
		document.getElementById("simulink_version").innerText = "No simulink model version found";
        console.log(res.err);
	} else {
		document.getElementById("simulink_version").innerText = res.version;
	}
}, false);