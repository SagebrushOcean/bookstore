const confirmNumber = document.getElementById("confirm-number");
const info = document.getElementById("info");
const inputCode = document.getElementById("input-code");
const phone = document.getElementById("phone");
const submit = document.getElementById("submit");

function validate(inputIDs) {
    let inputID, rest;
    [inputID, ...rest] = inputIDs;
    if (!inputID) {
        inputCode.innerHTML = 'Введите код, отправленный на номер <br>'+phone.value+':';
        info.classList.add('hide');
        confirmNumber.classList.remove('hide');
        submit.textContent = 'Подтвердить';
        return true
    }
    const input = document.getElementById(inputID);
    if (input.checkValidity()){
        return validate(rest)
    }else{
        input.reportValidity()
        return false
    }
}

submit.addEventListener("click", (event) => {
    if (!validate(["name", "phone", "email", "password", "confirm_password"])) {
        event.preventDefault();
    }
});