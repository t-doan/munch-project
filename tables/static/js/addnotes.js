function clickAddNote(some_id) {
  document.getElementById("textbox" + some_id).className="show";
  document.getElementById("note" + some_id).className="hide";
}
function clickAddInstructionNote() {
  document.getElementById("instructionBox").className="show";
  document.getElementById("instructionclick").className="hide";
}
function enableChange1(new_value, old_value) {
  if (new_value.value != old_value) {
    document.getElementById("save").disabled = false;
    document.getElementById("checkout").disabled = true;
  }
  else {
    document.getElementById("save").disabled = true;
    document.getElementById("checkout").disabled = false;
  }
}
function enableChange2(txt) {
  if (txt.value != '') {
    document.getElementById("save").disabled = false;
    document.getElementById("checkout").disabled = true;
  }
  else {
    document.getElementById("save").disabled = true;
    document.getElementById("checkout").disabled = false;
  }
}
