document.getElementById('btn_go').addEventListener('click', function(e) {
    e.preventDefault(); // Prevent default form submission behavior

    // Get the selected values from the dropdowns
    var select_s_r = document.getElementById('select_s_r').value;
    var select_level = document.getElementById('select_level').value;

    // Check the selected values and redirect accordingly
    if (select_level === '1') {
        // If "School" is selected
        if (select_s_r === '1') {
            // If "Stats" is selected, redirect to gc1
            window.location.href = '/student_dashboard/gc1'; // Replace 'gc1' with the URL of the stats page for school
        } else if (select_s_r === '2') {
            // If "Report" is selected, redirect to report_c1
            window.location.href = '/student_dashboard/report_c1'; // Replace 'report_c1' with the URL of the report page for school
        } else {
            // If neither "Stats" nor "Report" is selected, show an error message
            alert('Please select a view.');
        }
    } else if (select_level === '2') {
        // If "Under Graduation" is selected
        if (select_s_r === '1') {
            // If "Stats" is selected, redirect to g_ug_sem_1
            window.location.href = '/student_dashboard/g_ug_sem_1'; // Replace 'g_ug_sem_1' with the URL of the stats page for Under Graduation
        } else if (select_s_r === '2') {
            // If "Report" is selected, redirect to report_ug_sem_1
            window.location.href = '/student_dashboard/report_ug_sem_1'; // Replace 'report_ug_sem_1' with the URL of the report page for Under Graduation
        } else {
            // If neither "Stats" nor "Report" is selected, show an error message
            alert('Please select a view.');
        }
    } else if (select_level === '3') {
        // If "Post Graduation" is selected
        if (select_s_r === '1') {
            // If "Stats" is selected, redirect to g_pg_sem_1
            window.location.href = '/student_dashboard/g_pg_sem_1'; // Replace 'g_pg_sem_1' with the URL of the stats page for Post Graduation
        } else if (select_s_r === '2') {
            // If "Report" is selected, redirect to report_pg_sem_1
            window.location.href = '/student_dashboard/report_pg_sem_1'; // Replace 'report_pg_sem_1' with the URL of the report page for Post Graduation
        } else {
            // If neither "Stats" nor "Report" is selected, show an error message
            alert('Please select a view.');
        }
    } else {
        // show an error message
        if (select_s_r === '0') {
            // If neither "Stats" nor "Report" is selected, show an error message
            alert('Please select a view.');
        } else {
            // If Education Level is not selected, show an error message
        alert('Please select Educational Level.');
        }
    }
});
