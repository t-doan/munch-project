function showShipping(checkbox) {
  if (checkbox.checked) {
    document.getElementById("shipping-content").className="hide";
  }
  else {
    document.getElementById("shipping-content").className="show";
  }
}
function showBillingCheck(checkbox) {
  if (checkbox.checked) {
    document.getElementById("billing-check").className="hide";
  }
  else {
    document.getElementById("billing-check").className="show";
  }
}
function showBilling(checkbox) {
  if (checkbox.checked) {
    document.getElementById("billing-content").className="hide";
  }
  else {
    document.getElementById("billing-content").className="show";
  }
}
