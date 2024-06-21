document.querySelectorAll('.editable').forEach(cell => {
    cell.addEventListener('input', function (e) {
        if (!/^\d*\.?\d*$/.test(e.target.innerText)) {
            e.target.innerText = e.target.innerText.replace(/[^\d.]/g, '');
        }
    });
});

document.querySelectorAll('.tabela_editavel tr').forEach(row => {
    const checkboxes = row.querySelectorAll('.checkbox');
    const container = document.getElementById('selectContainer');
    
    const updateContainerDisplay = () => {
        const anySecondChecked = document.querySelectorAll('.tabela_editavel tr td:nth-child(6) .checkbox:checked').length > 0;
        container.style.display = anySecondChecked ? 'flex' : 'none';
    };

    checkboxes.forEach((checkbox, index) => {
        checkbox.addEventListener('change', () => {
            if (checkbox.checked) {
                checkboxes.forEach((cb, cbIndex) => {
                    if (index !== cbIndex) {
                        cb.checked = false;
                    }
                });
            }
            updateContainerDisplay();
        });
    });
});