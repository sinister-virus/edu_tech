// Used in: form_student_info.html
document.getElementById('same_as_permanent').addEventListener('change', function() {
    if (this.checked) {
        document.getElementById('pa_line_1').value = document.getElementById('ca_line_1').value;
        document.getElementById('pa_line_2').value = document.getElementById('ca_line_2').value;
        document.getElementById('pa_line_3').value = document.getElementById('ca_line_3').value;
        document.getElementById('pa_city').value = document.getElementById('ca_city').value;
        document.getElementById('pa_district').value = document.getElementById('ca_district').value;
        document.getElementById('pa_state').value = document.getElementById('ca_state').value;
        document.getElementById('pa_pincode').value = document.getElementById('ca_pincode').value;
    } else {
        document.getElementById('pa_line_1').value = '';
        document.getElementById('pa_line_2').value = '';
        document.getElementById('pa_line_3').value = '';
        document.getElementById('pa_city').value = '';
        document.getElementById('pa_district').value = '';
        document.getElementById('pa_state').value = '';
        document.getElementById('pa_pincode').value = '';
    }
});
