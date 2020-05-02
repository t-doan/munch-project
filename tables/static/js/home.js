function inputAddress(addr) {
  if (addr.length === 0) {
    document.getElementById("enter_address_btn").disabled = true;
  }
  else {
    document.getElementById("enter_address_btn").disabled = false;
  }
}
