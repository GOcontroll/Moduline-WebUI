document.addEventListener('DOMContentLoaded', async function() {
    const simulink_request = await fetch('/api/get_sim_ver');
	$('#simulink_version').html(await simulink_request.json());

	const wifi_request = await fetch('/api/get_wifi');
	console.log(await wifi_request.json());

}, false);