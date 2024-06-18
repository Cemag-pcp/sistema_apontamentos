document.addEventListener('DOMContentLoaded', function() {
    const addButton = document.getElementById('addButton');
    const removeButton = document.getElementById('removeButton');
    const addButtonReinspecao = document.getElementById('addButtonTubos');
    const removeButtonReinspecao = document.getElementById('removeButtonTubos');
    let counter = 1;

    // Função para adicionar causa
    function adicionarCausa(inputNaoConformidades_estamparia,selectContainer,addcause,reinspecao,tipos_causas_estamparia) {

        const selectBlock = document.querySelector('.selectBlock').cloneNode(true);
        const quantidadeBlock = document.querySelector('.quantidadeBlock').cloneNode(true);

        const tipos_causas = document.getElementById(tipos_causas_estamparia)

        tipos_causas.value = counter + 1;

        // Update IDs and names for the cloned elements
        selectBlock.id = `selectBlock-${counter}`;
        quantidadeBlock.id = `quantidadeBlock-${counter}`;

        const selectElement = selectBlock.querySelector('select');
        const inputElement = quantidadeBlock.querySelector('input');

        selectElement.id = `causasCilindro${reinspecao}-${counter}`;
        selectElement.name = `causasCilindro${reinspecao}-${counter}`;

        inputElement.id = `quantidade_causas_cilindro${reinspecao}-${counter}`;
        inputElement.name = `quantidade_causas_cilindro${reinspecao}-${counter}`;

        // Calculate the value for the new input element
        const inputNaoConformidades = document.getElementById(inputNaoConformidades_estamparia);
        const valorNaoConformidades = inputNaoConformidades ? parseFloat(inputNaoConformidades.value) || 0 : 0;

        let totalCausas = 0;
        for (let i = 0; i < counter; i++) {
            const causaAnterior = document.getElementById(`quantidade_causas_estamparia${reinspecao}-${i}`);
            totalCausas += causaAnterior ? parseFloat(causaAnterior.value) || 0 : 0;
        }

        const novoValor = valorNaoConformidades - totalCausas;

        // Set the calculated value
        inputElement.value = novoValor;

        // Insert cloned elements into the DOM
        selectContainer.insertBefore(selectBlock, addcause.parentNode);
        selectContainer.insertBefore(quantidadeBlock, addcause.parentNode);

        counter++;

    }

    // Função para remover causa
    function removerCausa(tipos_causas_estamparia,remove, qtd) {
        const selectBlocks = document.querySelectorAll('.selectBlock');
        const quantidadeBlocks = document.querySelectorAll('.quantidadeBlock');
        const tipos_causas = document.getElementById(tipos_causas_estamparia)

        tipos_causas.value = counter - 1;

        if (selectBlocks.length > 1 && quantidadeBlocks.length > 1) {
            selectBlocks[selectBlocks.length - qtd].remove();
            quantidadeBlocks[quantidadeBlocks.length - qtd].remove();
            counter--;
        }

        console.log(selectBlocks.length)

        if (selectBlocks.length <= 3 && quantidadeBlocks.length <= 3) {
            remove.disabled = true;  // Disable the remove button if there's only one block left
        }
    }

    // Adicionando eventos de clique aos botões
    addButton.addEventListener('click', function () {
        let selectContainer = document.getElementById('selectContainer');
        adicionarCausa('nao_conformidade_cilindro',selectContainer,addButton,'C','tipos_causas_cilindro');
        removeButton.disabled = false;
    });
    removeButton.addEventListener('click', function () {
        removerCausa('tipos_causas_cilindro',removeButton,2)
    });
    
    addButtonReinspecao.addEventListener('click', function () {
        let selectContainerReinspecao = document.getElementById('selectContainerTubos');
        adicionarCausa('nao_conformidade_tubo',selectContainerReinspecao,addButtonReinspecao,'T','tipos_causas_tubo');
        removeButtonReinspecao.disabled = false;
    });
    removeButtonReinspecao.addEventListener('click', function () {
        removerCausa('tipos_causas_tubo',removeButtonReinspecao,1)
    });

});
