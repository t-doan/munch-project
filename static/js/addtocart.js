// var URL = "{% url 'projects:Unread' %}";
// var obj = JSON.parse({{ chosen_items|safe|escape }});
// alert("Wowee");
// alert(obj.name === "John");

// function showAlert(){
//   alert("Show alert");
// }

function clickAddToCart(id) {
  document.getElementById("quantity" + id).className="show";
  document.getElementById("btn-confirm" + id).className="show";
  document.getElementById("btn" + id).className="hide";
  alert("Clicked add to cart for item with id = " + id);
}

function confirm(id) {
  document.getElementById("quantity" + id).className="hide";
  document.getElementById("btn-confirm" + id).className="hide";
  document.getElementById("btn" + id).className="show";
  const val = document.getElementById("quantity" + id).value;
  alert("Confirm clicked for item with id = " + id + " and val = " + val);
}
