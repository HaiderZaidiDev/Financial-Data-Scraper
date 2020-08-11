window.onload = function priceStatus() {
  var status = document.getElementById("priceStatus");
  statusContent = status.textContent;
  if (statusContent.startsWith(' -')) {
    status.style.color = 'red';
  }
  else {
    status.style.color = 'green';
  }
}

function loadingPage() {
  var div = document.getElementById("loading-wrapper")
  div.style.display = "block";

  var body = document.getElementsByTagName("body")
  body.style.overflow = "hidden"
}
