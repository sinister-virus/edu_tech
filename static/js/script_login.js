function login() {
  // Get the values from the input fields
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const role = document.getElementById('role').value;

  // Check if either username, password, or role is empty
  if (!username.trim() || !password.trim() || !role.trim()) {
    alert('Please enter username, password and select a role.');
    return;
  }

  // Implement your actual login logic here based on roles
}