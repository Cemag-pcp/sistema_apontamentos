document.addEventListener('DOMContentLoaded', function() {
    const addButton = document.getElementById('addButton');
    const addButtonReinspecao = document.getElementById('addButtonReinspecao');
    const removeButton = document.getElementById('removeButton');
    const removeButtonReinspecao = document.getElementById('removeButtonReinspecao');
    let counter = 1;

    // Função para adicionar causa
    function adicionarCausa(inputNaoConformidades_estamparia,selectContainer,addcause,reinspecao) {

        console.log("Entrou")
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

        selectElement.id = `causasEstamparia${reinspecao}-${counter}`;
        selectElement.name = `causasEstamparia${reinspecao}-${counter}`;
        inputElement.id = `quantidade_causas_estamparia${reinspecao}-${counter}`;
        inputElement.name = `quantidade_causas_estamparia${reinspecao}-${counter}`;
        fileInputElement.id = `inputGroupFile_estamparia${reinspecao}-${counter}`;

        // Calculate the value for the new input element
        const inputNaoConformidades = document.getElementById(inputNaoConformidades_estamparia);
        const valorNaoConformidades = inputNaoConformidades ? parseFloat(inputNaoConformidades.value) || 0 : 0;

        let totalCausas = 0;
        for (let i = 0; i < counter; i++) {
            const causaAnterior = document.getElementById(`quantidade_causas_estamparia${reinspecao}-${i}`);
            console.log(causaAnterior)
            totalCausas += causaAnterior ? parseFloat(causaAnterior.value) || 0 : 0;
        }

        const novoValor = valorNaoConformidades - totalCausas;

        console.log(totalCausas)

        console.log(novoValor)

        // Set the calculated value
        inputElement.value = novoValor;

        // Insert cloned elements into the DOM
        selectContainer.insertBefore(selectBlock, addcause.parentNode);
        selectContainer.insertBefore(quantidadeBlock, addcause.parentNode);
        selectContainer.insertBefore(customFileBlock, addcause.parentNode);

        counter++;

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
    function removerCausa(tipos_causas_estamparia,remove, qtd) {
        const selectBlocks = document.querySelectorAll('.selectBlock');
        const quantidadeBlocks = document.querySelectorAll('.quantidadeBlock');
        const customFileBlocks = document.querySelectorAll('.customFileBlock');
        const tipos_causas = document.getElementById(tipos_causas_estamparia)

        tipos_causas.value = counter - 1;

        if (selectBlocks.length > 1 && quantidadeBlocks.length > 1 && customFileBlocks.length > 1) {
            selectBlocks[selectBlocks.length - 1].remove();
            quantidadeBlocks[quantidadeBlocks.length - qtd].remove();
            customFileBlocks[customFileBlocks.length - qtd].remove();
            counter--;
        }

        if (selectBlocks.length <= 3 && quantidadeBlocks.length <= 3 && customFileBlocks.length <= 3) {
            remove.disabled = true;  // Disable the remove button if there's only one block left
        }
    }

    
    // Adicionando eventos de clique aos botões
    addButton.addEventListener('click', function () {
        let selectContainer = document.getElementById('selectContainer');
        adicionarCausa('inputNaoConformidades_estamparia',selectContainer,addButton,'');
        removeButton.disabled = false;
    });
    removeButton.addEventListener('click', function () {
        removerCausa('tipos_causas_estamparia',removeButton,2)
    });
    addButtonReinspecao.addEventListener('click', function () {
        let selectContainerReinspecao = document.getElementById('selectContainerReinspecao');
        adicionarCausa('inputReinspecionadasNaoConformidades_estamparia',selectContainerReinspecao,addButtonReinspecao,'R');
        removeButtonReinspecao.disabled = false;
    });
    removeButtonReinspecao.addEventListener('click', function () {
        removerCausa('tipos_causas_estamparia_reinspecao',removeButtonReinspecao,1)
    });

    // Adicionando evento de mudança aos campos de arquivo existentes
    const fileInputs = document.querySelectorAll('.customFile');
    fileInputs.forEach(function(fileInput) {
        const fileLabel = fileInput.querySelector('.custom-file-label');
        fileInput.querySelector('.custom-file-input').addEventListener('change', function() {
            const files = this.files;
            if (files.length > 0) {
                fileLabel.textContent = `${files.length} arquivo(s) selecionado(s)`;
            } else {
                fileLabel.textContent = '0 arquivos';
            }
        });
    });
});
