function toggle(source) {
  checkboxes = document.getElementsByName('item_id');
  for(var i in checkboxes)
    checkboxes[i].checked = source.checked;
}

function validate(inputID) {
  const input = document.getElementById(inputID);
  input.setCustomValidity("");
  if (document.querySelectorAll("input[type=checkbox]:checked").length==0) {
    input.setCustomValidity("Чтобы сделать заказ выберите хотя бы один предмет из корзины.");
  }
  input.reportValidity();
}

const submit = document.getElementById("submit");
submit.addEventListener("click", (event) => {
  validate("submit");
});

const buttons = document.querySelectorAll('form button:not([type="submit"])');
for (i = 0; i < buttons.length; i++) {
  buttons[i].addEventListener('click', function(e) {
    e.preventDefault();
  });
}