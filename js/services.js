async function set_service(service) {
	//get what the next state of wifi should be
	let set_state = {};
	if (!$("#"+service).prop("checked")) { //why does this work with a not?
		set_state.new_state = false;
	} else {
		set_state.new_state = true;
	}
	set_state.service = service;
	//try to make it a reality
	try{
		const resp = await post_json("/api/set_service", set_state);
		if (resp.err != undefined) {
			//server failed to toggle wifi
			$('#'+service).prop("checked",!set_state.new_state);
			alert("Could not toggle " + service + ":\n" + resp.err);
		}
	} catch(err) {
		alert("Could not toggle " + service + ":\n" + err);
		$('#'+service).prop("checked",!set_state.new_state);
	}
}

async function get_service(service) {
	try{
		const resp = await post_json("/api/get_service", service);
		if (resp.state) {
			$('#'+service).prop("checked",true);
		} else {
			$('#'+service).prop("checked",false);
		}
	} catch(err) {
		alert("Could get the state of " + service + ":\n" + err);
	}
}

document.addEventListener('DOMContentLoaded', async function() {
	const services = $(".service-cb");
	for (var i = 0; i < services.length; i++) {
		id = services[i].attributes.id.value;
		get_service(id);
	}
}, false);