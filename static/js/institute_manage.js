const userTypeSelect = document.getElementById("user_type");
const continueBtn = document.getElementById("go");

continueBtn.addEventListener("click", (event) => {
  const selectedUserType = userTypeSelect.value;
    if (selectedUserType === "0") {
        event.preventDefault();
        alert('Please select a role.');
    }

    else {
    if
    (selectedUserType === "student") {
      window.location.href = "/student_register";
    }
    if (selectedUserType === "institute") {
      window.location.href = "/institute_register";
    }
    else if (selectedUserType === "admin") {
      window.location.href = "/admin_register";
    }
  }
}
);