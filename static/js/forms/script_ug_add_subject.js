let subjectCount = 6;

function addSubject() {
    if (subjectCount < 20) {
        subjectCount++;
        // Get the next subject field to display
        let nextSubject = document.getElementById('sub_' + subjectCount);
        // Check if the next subject field exists
        if (nextSubject) {
            // Display the next subject field
            nextSubject.classList.remove('hidden');
        } else {
            alert('Maximum limit of 20 subjects reached.');
        }
    } else {
        alert('Maximum limit of 20 subjects reached.');
    }
}
