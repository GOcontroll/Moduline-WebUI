function alert_class_switch(elem, newClass) {
  elem.classList.remove("ok", "info", "fail");
  elem.classList.add(newClass, "fade-in");
  setTimeout(() => {
    elem.classList.remove("fade-in");
  }, 500);
  setTimeout(() => {
    elem.classList.remove("ok", "info", "fail");
    elem.innerText = "";
  }, 5000);
}

async function post_json(url, data) {
  return (await fetch(url,
    {
      method: 'POST',
      body: JSON.stringify(data),
      headers: { "Content-type": "application/json; charset=UTF-8" }
    }
  )).json()
}
