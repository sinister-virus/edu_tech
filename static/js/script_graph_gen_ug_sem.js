// Initiate the graph generation
document.getElementById('graph_gen').addEventListener('click', function(e) {
    e.preventDefault();
    var selected_class = document.getElementById('select_class').value;
    window.location.href = '/student_dashboard/g_ug_sem_' + selected_class;
});
