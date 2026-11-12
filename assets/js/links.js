// Links zu anderen Websites öffnen sich in einem neuen Tab.
// Links innerhalb von benja.at bleiben im selben Tab.
document.querySelectorAll("a[href]").forEach(function (link) {
  var istAuswaerts = (link.protocol === "http:" || link.protocol === "https:") &&
                     link.hostname !== window.location.hostname;
  if (istAuswaerts) {
    link.target = "_blank";
    link.rel = "noopener";
  }
});
