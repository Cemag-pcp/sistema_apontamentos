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
    const inputConformidades = document.getElementById('inputConformidades_estamparia');
    const inputNaoConformidades = document.getElementById('inputNaoConformidades_estamparia');
    const inputOutraCausa = document.getElementById('outraCausa_estamparia');

    const updateContainerDisplay = () => {
        const anySecondChecked = document.querySelectorAll('.tabela_editavel tr td:nth-child(6) .checkbox:checked').length > 0;
        container.style.display = anySecondChecked ? 'flex' : 'none';
    };

    const updateOutraCausa = () => {
        if (parseInt(inputNaoConformidades.value) > 0) {
            inputOutraCausa.disabled = false;
        } else {
            inputOutraCausa.disabled = true;
        }
    };

    checkboxes.forEach((checkbox, index) => {
        checkbox.addEventListener('change', () => {
            if (index === 0) { // Primeiro checkbox
                if (checkbox.checked) {
                    if (checkboxes[1].checked) {
                        inputNaoConformidades.value = parseInt(inputNaoConformidades.value) - 1;
                    }
                    checkboxes[1].checked = false;
                    inputConformidades.value = parseInt(inputConformidades.value) + 1;
                } else {
                    inputConformidades.value = parseInt(inputConformidades.value) - 1;
                }
            } else { // Segundo checkbox
                if (checkbox.checked) {
                    if (checkboxes[0].checked) {
                        inputConformidades.value = parseInt(inputConformidades.value) - 1;
                    }
                    checkboxes[0].checked = false;
                    inputNaoConformidades.value = parseInt(inputNaoConformidades.value) + 1;
                } else {
                    inputNaoConformidades.value = parseInt(inputNaoConformidades.value) - 1;
                }
            }
            updateContainerDisplay();
            updateOutraCausa();
        });
    });

    // Initialize the state of the inputOutraCausa
    updateOutraCausa();
});




