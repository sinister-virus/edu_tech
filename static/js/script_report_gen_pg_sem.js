// Initiate the graph generation
document.getElementById('report_gen').addEventListener('click', function(e) {
    e.preventDefault();
    var selected_class = document.getElementById('select_class').value;
    window.location.href = '/student_dashboard/report_pg_sem_' + selected_class;
});
