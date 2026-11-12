// Schließt das Menü, wenn man daneben klickt oder die Esc-Taste drückt.
document.addEventListener("click", function (event) {
  var menu = document.querySelector(".menu");
  if (menu && menu.open && !menu.contains(event.target)) {
    menu.open = false;
  }
});
document.addEventListener("keydown", function (event) {
  var menu = document.querySelector(".menu");
  if (event.key === "Escape" && menu && menu.open) {
    menu.open = false;
    menu.querySelector("summary").focus();
  }
});
