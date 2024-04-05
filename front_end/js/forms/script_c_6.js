
let subjectCount = 6;

function addSubject() {
    if (subjectCount <= 20) {
        const subjectFields = document.getElementById('subjectFields');

        subjectFields.appendChild(document.createElement('hr'));
        // subject_name
        const label1 = document.createElement('label');
        label1.htmlFor = `c_6_sub_${subjectCount}_name`;
        label1.textContent = `Subject ${subjectCount} Name:`;
        subjectFields.appendChild(label1);

        subjectFields.appendChild(document.createElement('br'));

        const input1 = document.createElement('input');
        input1.type = 'text';
        input1.id = `c_6_sub_${subjectCount}_name`;
        input1.name = `c_6_sub_${subjectCount}_name`;
        subjectFields.appendChild(input1);

        subjectFields.appendChild(document.createElement('br'));

        // subject_marks_obtained
        const label2 = document.createElement('label');
        label2.htmlFor = `c_6_sub_${subjectCount}_marks_obtained`;
        label2.textContent = `Subject ${subjectCount} Marks Obtained:`;
        subjectFields.appendChild(label2);

        subjectFields.appendChild(document.createElement('br'));

        const input2 = document.createElement('input');
        input2.type = 'text';
        input2.id = `c_6_sub_${subjectCount}_marks_obtained`;
        input2.name = `c_6_sub_${subjectCount}_marks_obtained`;
        subjectFields.appendChild(input2);

        subjectFields.appendChild(document.createElement('br'));

        // subject_total_marks
        const label3 = document.createElement('label');
        label3.htmlFor = `c_6_sub_${subjectCount}_total_marks`;
        label3.textContent = `Subject ${subjectCount} Total Marks:`;
        subjectFields.appendChild(label3);

        subjectFields.appendChild(document.createElement('br'));

        const input3 = document.createElement('input');
        input3.type = 'text';
        input3.id = `c_6_sub_${subjectCount}_total_marks`;
        input3.name = `c_6_sub_${subjectCount}_total_marks`;
        subjectFields.appendChild(input3);

        subjectFields.appendChild(document.createElement('br'));

        subjectCount++;
    } else {
        alert('Maximum limit of 20 subjects reached.');
    }
}