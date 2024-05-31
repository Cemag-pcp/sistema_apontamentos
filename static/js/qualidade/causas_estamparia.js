document.addEventListener('DOMContentLoaded', function() {
    const addButton = document.getElementById('addButton');
    const removeButton = document.getElementById('removeButton');
    const selectContainer = document.getElementById('selectContainer');
    let counter = 1;

    // Função para adicionar causa
    function adicionarCausa() {
        const selectBlock = document.querySelector('.selectBlock').cloneNode(true);
        const quantidadeBlock = document.querySelector('.quantidadeBlock').cloneNode(true);
        const customFileBlock = document.querySelector('.customFileBlock').cloneNode(true);

        const tipos_causas_estamparia = document.getElementById('tipos_causas_estamparia')

        tipos_causas_estamparia.value = counter + 1;

        // Update IDs and names for the cloned elements
        selectBlock.id = `selectBlock-${counter}`;
        quantidadeBlock.id = `quantidadeBlock-${counter}`;
        customFileBlock.id = `customFileBlock-${counter}`;

        const selectElement = selectBlock.querySelector('select');
        const inputElement = quantidadeBlock.querySelector('input');
        const fileInputElement = customFileBlock.querySelector('input');
        const fileLabelElement = customFileBlock.querySelector('label');

        fileLabelElement.textContent = '0 arquivos';

        selectElement.id = `causasEstamparia-${counter}`;
        selectElement.name = `causasEstamparia-${counter}`;
        inputElement.id = `quantidade_causas_estamparia-${counter}`;
        inputElement.name = `quantidade_causas_estamparia-${counter}`;
        fileInputElement.id = `inputGroupFile_estamparia-${counter}`;

        // Calculate the value for the new input element
        const inputNaoConformidades = document.getElementById('inputNaoConformidades_estamparia');
        const valorNaoConformidades = inputNaoConformidades ? parseFloat(inputNaoConformidades.value) || 0 : 0;

        let totalCausas = 0;
        for (let i = 0; i < counter; i++) {
            const causaAnterior = document.getElementById(`quantidade_causas_estamparia-${i}`);
            totalCausas += causaAnterior ? parseFloat(causaAnterior.value) || 0 : 0;
        }

        const novoValor = valorNaoConformidades - totalCausas;

        // Set the calculated value
        inputElement.value = novoValor;

        // Insert cloned elements into the DOM
        selectContainer.insertBefore(selectBlock, addButton.parentNode);
        selectContainer.insertBefore(quantidadeBlock, addButton.parentNode);
        selectContainer.insertBefore(customFileBlock, addButton.parentNode);

        counter++;
        removeButton.disabled = false;  // Enable the remove button
        
        // Attach change event listener to file input
        fileInputElement.addEventListener('change', function() {
            const files = this.files;
            if (files.length > 0) {
                fileLabelElement.textContent = `${files.length} arquivo(s)`;
            } else {
                fileLabelElement.textContent = '0 arquivo';
            }
        });
    }

    // Função para remover causa
    function removerCausa() {
        const selectBlocks = document.querySelectorAll('.selectBlock');
        const quantidadeBlocks = document.querySelectorAll('.quantidadeBlock');
        const customFileBlocks = document.querySelectorAll('.customFileBlock');
        const tipos_causas_estamparia = document.getElementById('tipos_causas_estamparia')

        tipos_causas_estamparia.value = counter - 1;

        console.log(selectBlocks.length,quantidadeBlocks.length,customFileBlocks.length)

        if (selectBlocks.length > 1 && quantidadeBlocks.length > 1 && customFileBlocks.length > 1) {
            selectBlocks[selectBlocks.length - 1].remove();
            quantidadeBlocks[quantidadeBlocks.length - 1].remove();
            customFileBlocks[customFileBlocks.length - 1].remove();
            counter--;
        }

        if (selectBlocks.length <= 2 && quantidadeBlocks.length <= 2 && customFileBlocks.length <= 2) {
            removeButton.disabled = true;  // Disable the remove button if there's only one block left
        }
    }

    // Adicionando eventos de clique aos botões
    addButton.addEventListener('click', adicionarCausa);
    removeButton.addEventListener('click', removerCausa);

    // Adicionando evento de mudança aos campos de arquivo existentes
    const fileInputs = document.querySelectorAll('.customFile');
    fileInputs.forEach(function(fileInput) {
        const fileLabel = fileInput.querySelector('.custom-file-label');
        fileInput.querySelector('.custom-file-input').addEventListener('change', function() {
            const files = this.files;
            console.log(files)
            if (files.length > 0) {
                fileLabel.textContent = `${files.length} arquivo(s) selecionado(s)`;
            } else {
                fileLabel.textContent = '0 arquivos';
            }
        });
    });
});
