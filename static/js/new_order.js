const delivery1 = document.getElementById("delivery-1");

function validate(inputID) {
  const input = document.getElementById(inputID);
  input.setCustomValidity("");
  if (delivery1.checked && !input.value) {
    input.setCustomValidity("Заполните это поле.");
  }
  input.reportValidity();
}

submit.addEventListener("click", (event) => {
    validate("address");
});