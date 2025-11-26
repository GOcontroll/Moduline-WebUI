async function try_login(event) {
  event.preventDefault(); // Prevent the default form submission
  const passkey_field = document.getElementById("passkey");
  const result = document.getElementById("set_login_result");
  try {
    const resp = await post_json("/login", passkey_field.value)
    if (resp.err) {
      alert_class_switch(result, "fail");
      result.innerText = "Error: " + resp.err;
      return;
    }
    window.location.href = "/static/home.html";
  } catch (err) {
    alert_class_switch(result, "fail");
    result.innerText = "could not login, invalid response";
    console.log("could not login:\n" + err);
  }
}