const userTypeSelect = document.getElementById("user_type");
const continueBtn = document.getElementById("continue_btn");
const tncCheckbox = document.getElementById("tnc_cb");
const errorMsg = document.createElement('p');
errorMsg.style.color = 'red';

// Redirect based on user type
continueBtn.addEventListener("click", (event) => {
  const selectedUserType = userTypeSelect.value;

  if (!tncCheckbox.checked) {
    event.preventDefault();
    errorMsg.textContent = 'Please read all the terms and conditions and tick the checkbox.';
    if (!document.body.contains(errorMsg)) {
      continueBtn.parentNode.insertBefore(errorMsg, continueBtn.nextSibling);
    }
  } else if (selectedUserType === "default") {
    event.preventDefault();
    errorMsg.textContent = 'Please select a role.';
    if (!document.body.contains(errorMsg)) {
      continueBtn.parentNode.insertBefore(errorMsg, continueBtn.nextSibling);
    }
  } else {
    if (document.body.contains(errorMsg)) {
      errorMsg.remove();
    }
    if (selectedUserType === "student") {
      window.location.href = "/student_register";
    }
    if (selectedUserType === "institute") {
      window.location.href = "/institute_register";
    }
    else if (selectedUserType === "admin") {
      window.location.href = "/admin_register";
    }
  }
});