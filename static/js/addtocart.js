function clickAddToCart(id) {
  document.getElementById("quantity" + id).className="show";
  document.getElementById("btn-confirm" + id).className="show";
  document.getElementById("btn" + id).className="hide";
}

function confirm(id) {
  document.getElementById("quantity" + id).className="hide";
  document.getElementById("btn-confirm" + id).className="hide";
  document.getElementById("btn" + id).className="show";
}
