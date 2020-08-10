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
