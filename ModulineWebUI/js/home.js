document.addEventListener('DOMContentLoaded', async function () {
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


async function set_passkey() {
    const pass1 = document.getElementById("passkey1");
    const pass2 = document.getElementById("passkey2");
    const result = document.getElementById("new_passkey_result");
    if (pass1.value != pass2.value) {
        result.innerText = "Could not set new passkey, entries don't match.";
        result.className = "fail";
        return;
    }
    if (!(pass1.value.length > 6)) {
        result.innerText = "Could not set new passkey, new passkey must be longer than 6 characters.";
        result.className = "fail";
        return;
    }
    try {
        const response = await post_json("/api/set_passkey", { "passkey": pass1.value });
        if (response.err) {
            result.innerText = response.err;
            result.className = "fail";
            console.log(response.deets);
            return;
        }
        result.innerText = "Succesfully changed the passkey!"
        result.className = "ok"
        return
    } catch (err) {
        result.innerText = "Could not set new passkey, unexpected response from server";
        result.className = "fail";
        console.log(err);
        return;
    }
}

async function toggle_pass() {
    const pass1 = document.getElementById("passkey1");
    const pass2 = document.getElementById("passkey2");
    if (pass1.getAttribute("type") === "password") {
        pass1.setAttribute("type", "text");
        pass2.setAttribute("type", "text");
    } else if (pass1.getAttribute("type") === "text") {
        pass1.setAttribute("type", "password");
        pass2.setAttribute("type", "password");
    }
}