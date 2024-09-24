document.querySelectorAll('.editable').forEach(cell => {
    cell.addEventListener('input', function (e) {
        if (!/^\d*\.?\d*$/.test(e.target.innerText)) {
            e.target.innerText = e.target.innerText.replace(/[^\d.]/g, '');
        }
    });
});

function initializeCheckboxLogic(tableSelector, containerId, inputConformidadesId, inputNaoConformidadesId, inputOutraCausaId) {
    // Seleciona as linhas da tabela especificada
    document.querySelectorAll(`${tableSelector} tr`).forEach(row => {
        const checkboxes = row.querySelectorAll('.checkbox');
        const container = document.getElementById(containerId);
        const inputConformidades = document.getElementById(inputConformidadesId);
        const inputNaoConformidades = document.getElementById(inputNaoConformidadesId);
        const inputOutraCausa = document.getElementById(inputOutraCausaId);

        const updateContainerDisplay = () => {
            const anySecondChecked = document.querySelectorAll(`${tableSelector} tr td:nth-child(6) .checkbox:checked`).length > 0;
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

        // Inicializa o estado do inputOutraCausa
        updateOutraCausa();
    });
}




