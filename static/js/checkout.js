function copy() {
  document.deliveryAddress.value = document.billingAddress.value;
  document.deliveryCity.value = document.billingCity.value;
  document.deliveryState.value = document.billingState.value;
  document.deliveryZipcode.value = document.billingZipcode.value;
  document.getElementById('click').className='hide';
}
