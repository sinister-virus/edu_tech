const userTypeSelect = document.getElementById("user_type");
      const continueBtn = document.getElementById("continue_btn");

      // Redirect based on user type
      continueBtn.addEventListener("click", () => {
        const selectedUserType = userTypeSelect.value;
        if (selectedUserType === "student") {
          window.location.href = "../Authentication/register_student.html";
        }
        if (selectedUserType === "institute") {
          window.location.href = "../Authentication/register_institute.html";
        }
        else if (selectedUserType === "admin") {
          window.location.href = "../Authentication/register_admin.html";
        }
      });