export function alert_class_switch(elem, newClass) {
  elem.classList.remove("ok", "info", "fail");
  elem.classList.add(newClass, "fade-in");
  setTimeout(() => {
    elem.classList.remove("fade-in");
  }, 500);
}