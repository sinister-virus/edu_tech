let subjectCount = 6;

function addSubject() {
    if (subjectCount <= 15) {
        // Get the subject fields
        const subjectName = document.getElementById(`c_1_sub_${subjectCount}_name`);
        const subjectMarksObtained = document.getElementById(`c_1_sub_${subjectCount}_marks_obtained`);
        const subjectTotalMarks = document.getElementById(`c_1_sub_${subjectCount}_total_marks`);

        // Remove the 'hidden' class to make the subject fields visible
        subjectName.classList.remove('hidden');
        subjectMarksObtained.classList.remove('hidden');
        subjectTotalMarks.classList.remove('hidden');

        subjectCount++;
    } else {
        alert('Maximum limit of 15 subjects reached.');
    }
}
