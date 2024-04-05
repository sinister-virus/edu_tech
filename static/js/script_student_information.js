const form = document.querySelector('form');

form.addEventListener('submit', event => {
  const requiredFields = form.querySelectorAll('input[required], textarea[required]');
  const emptyFields = [];

  requiredFields.forEach(field => {
    if (!field.value.trim()) {
      emptyFields.push(field);
    }
  });

  if (emptyFields.length) {
    event.preventDefault();
    alert('Please fill in all required fields.');
  }
});