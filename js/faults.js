async function delete_codes() {
	var errors = [];
	$(".fault-code-sel").each( function () {
		if ($(this).prop("checked")) {
			errors.push($(this).prop("id"))
		}
	})
	if (errors.length){
		try {
			const res = await post_json("/api/delete_errors", errors);
			await update_errors();
		} catch(err) {
			console.log(err);
		}
	}
}

async function select_all_codes() {
	$(".fault-code-sel").each( function () {
		$(this).prop("checked", true);
	})
}

async function update_errors() {
	try {
		const errors_request = await (await fetch('/api/get_errors')).json();
		const fault_codes = document.getElementById("fault-codes")
		fault_codes.textContent = "";
		if (errors_request.err) {
			return;
		}
		for ( const fault of errors_request) {
			format_fault(fault);
		}
	} catch(err) {
		console.log(err);
	}
}

function format_fault(fault) {
	var desc = "";
	if (!fault.fc) {
		return "";
	}
	if (fault.desc) {
		desc = fault.desc;
	}
	const fault_codes = document.getElementById("fault-codes");
	const fault_templ = document.getElementById("fault-code");

	const new_row = fault_templ.content.cloneNode(true);
	let td = new_row.querySelectorAll("td");
	td[0].textContent = fault.fc;
	td[1].textContent = desc;
	
	let cb = new_row.querySelector("input")
	cb.id = fault.fc;
	fault_codes.appendChild(new_row);
}

document.addEventListener('DOMContentLoaded', async function() {
	await update_errors();
}, false);