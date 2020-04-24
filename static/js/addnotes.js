function clickAddNote(id) {
  document.getElementById("textbox" + id).className="show";
  document.getElementById("note" + id).className="hide";
}
function clickAddInstructionNote() {
  document.getElementById("instructionBox").className="show";
  document.getElementById("instructionclick").className="hide";
}
