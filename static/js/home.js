function inputAddress(addr) {
  if (addr === '') {
    enter_address_btn.disabled = true;
  }
  else {
    enter_address_btn.disabled = false;
  }
}
