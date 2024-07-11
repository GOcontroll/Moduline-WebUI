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
}, false);