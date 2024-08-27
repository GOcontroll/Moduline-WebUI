

document.addEventListener('DOMContentLoaded', async function () {
  const sn_request = fetch("/api/get_serial_number");
  const software_request = fetch('/api/get_software');
  const hardware_request = fetch("/api/get_hardware");
  const simulink_request = fetch('/api/get_sim_ver');
  var res = await (await sn_request).json();
  if (res.err) {
    document.getElementById("serial_number").innerText = "Not found";
    console.log(res.err);
  } else {
    document.getElementById("serial_number").innerText = res.sn;
  }
  res = await (await software_request).json();
  if (res.err) {
    document.getElementById("controller_software").innerText = "Not found";
    console.log(res.err);
  } else {
    document.getElementById("controller_software").innerText = res.version;
  }
  res = await (await hardware_request).json();
  if (res.err) {
    document.getElementById("controller_hardware").innerText = "Not found";
    console.log(res.err);
  } else {
    document.getElementById("controller_hardware").innerText = res.hardware;
  }
  res = await (await simulink_request).json();
  if (res.err) {
    document.getElementById("simulink_version").innerText = "Not found";
    console.log(res.err);
  } else {
    document.getElementById("simulink_version").innerText = res.version;
  }
}, false);


function alert_class_switch(elem, newClass) {
  elem.classList.remove("ok", "info", "fail");
  elem.classList.add(newClass, "fade-in");
  setTimeout(() => {
    elem.classList.remove("fade-in");
  }, 500);
}

async function set_passkey() {
  const pass1 = document.getElementById("passkey1");
  const pass2 = document.getElementById("passkey2");
  const result = document.getElementById("new_passkey_result");
  if (pass1.value != pass2.value) {
    result.innerText = "Could not set new passkey, entries don't match.";
    alert_class_switch(result, "info");
    return;
  }
  if (!(pass1.value.length > 6)) {
    result.innerText = "Could not set new passkey, new passkey must be longer than 6 characters.";
    alert_class_switch(result, "info");
    return;
  }
  try {
    const response = await post_json("/api/set_passkey", { "passkey": pass1.value });
    if (response.err) {
      result.innerText = response.err;
      alert_class_switch(result, "fail");
      console.log(response.deets);
      return;
    }
    result.innerText = "Successfully changed the passkey!"
    alert_class_switch(result, "ok");
    return
  } catch (err) {
    result.innerText = "Could not set new passkey, unexpected response from server";
    alert_class_switch(result, "fail");
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