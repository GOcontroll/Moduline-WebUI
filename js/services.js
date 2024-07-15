
const services_list = [
	["ssh", "SSH"],
	["go-simulink", "Simulink"],
	["nodered", "NodeRED"],
	["go-bluetooth", "Bluetooth server"],
	["go-upload-server", "Simulink upload server"],
	["go-auto-shutdown", "Auto shutdown"],
	["gadget-getty\@ttyGS0", "USB terminal"],
	["getty\@ttymxc2", "Serial terminal"]
]

async function set_service(service) {
	//get what the next state of wifi should be
	let set_state = {};
	if (!$("#service"+service).prop("checked")) { //why does this work with a not?
		set_state.new_state = false;
	} else {
		set_state.new_state = true;
	}
	set_state.service = services_list[service][0];
	//try to make it a reality
	try{
		const resp = await post_json("/api/set_service", set_state);
		if (resp.err != undefined) {
			//server failed to toggle wifi
			$('#service'+service).prop("checked",!set_state.new_state);
			alert("Could not toggle " + services_list[service][0] + ":\n" + resp.err);
		} else {
			$('#service'+service).prop("checked",resp.new_state);
		}
	} catch(err) {
		alert("Could not toggle " + services_list[service][0] + ":\n" + err);
		$('#service'+service).prop("checked",!set_state.new_state);
	}
}

async function get_service(service, index) {
	try{
		const resp = await post_json("/api/get_service", service[0]);
		const service_templ = document.getElementById("service");
		const services = document.getElementById("services");

		const new_service = service_templ.content.cloneNode(true);
		let p = new_service.querySelector("p");
		p.textContent = service[1];
		let cb = new_service.querySelector("input");
		cb.id = "service" + index;
		cb.setAttribute("onclick", "set_service("+index+")");
		cb.setAttribute("checked", resp.state);
		services.appendChild(new_service);
		
	} catch(err) {
		alert("Could get the state of " + service[0] + ":\n" + err);
	}
}

document.addEventListener('DOMContentLoaded', async function() {
	const services = document.getElementById("services");
	services.textContent = ""
	for (var i = 0; i < services_list.length; i++) {
		get_service(services_list[i], i)
	}
	// const services = $(".service-cb");
	// for (var i = 0; i < services.length; i++) {
	// 	id = services[i].attributes.id.value;
	// 	get_service(id);
	// }
}, false);