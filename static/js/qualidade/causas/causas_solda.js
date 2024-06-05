document.addEventListener('DOMContentLoaded', function() {
    const addButton = document.getElementById('addButtonSolda');
    const addButtonReinspecao = document.getElementById('addButtonReinspecaoSolda');
    const removeButton = document.getElementById('removeButtonSolda');
    const removeButtonReinspecao = document.getElementById('removeButtonReinspecaoSolda');

    const addButtonSoldaEdicao = document.getElementById('addButtonSoldaEdicao');
    const removeButtonSoldaEdicao = document.getElementById('removeButtonSoldaEdicao');
    let counter = 1;

    // Função para adicionar causa
    function adicionarCausa(inputNaoConformidades_estamparia,selectContainer,addcause,reinspecao,tipos_causas_estamparia) {

        const selectBlock = document.querySelector('.selectBlock').cloneNode(true);
        const quantidadeBlock = document.querySelector('.quantidadeBlock').cloneNode(true);
        const customFileBlock = document.querySelector('.customFileBlock').cloneNode(true);

        const tipos_causas = document.getElementById(tipos_causas_estamparia)

        tipos_causas.value = counter + 1;

        // Update IDs and names for the cloned elements
        selectBlock.id = `selectBlock-${counter}`;
        quantidadeBlock.id = `quantidadeBlock-${counter}`;
        customFileBlock.id = `customFileBlock-${counter}`;

        const selectElement = selectBlock.querySelector('select');
        const inputElement = quantidadeBlock.querySelector('input');
        const fileInputElement = customFileBlock.querySelector('input');
        const fileLabelElement = customFileBlock.querySelector('label');

        fileLabelElement.textContent = '0 arquivos';

        selectElement.id = `causasSolda${reinspecao}-${counter}`;
        selectElement.name = `causasSolda${reinspecao}-${counter}`;
        inputElement.id = `quantidade_causas_solda${reinspecao}-${counter}`;
        inputElement.name = `quantidade_causas_solda${reinspecao}-${counter}`;
        fileInputElement.id = `inputGroupFile_solda${reinspecao}-${counter}`;

        // Calculate the value for the new input element
        const inputNaoConformidades = document.getElementById(inputNaoConformidades_estamparia);
        const valorNaoConformidades = inputNaoConformidades ? parseFloat(inputNaoConformidades.value) || 0 : 0;

        let totalCausas = 0;
        for (let i = 0; i < counter; i++) {
            const causaAnterior = document.getElementById(`quantidade_causas_solda${reinspecao}-${i}`);
            totalCausas += causaAnterior ? parseFloat(causaAnterior.value) || 0 : 0;
        }

        const novoValor = valorNaoConformidades - totalCausas;

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
                fileLabelElement.textContent = '0 arquivos';
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

        console.log(selectBlocks.length)

        if (selectBlocks.length > 1 && quantidadeBlocks.length > 1 && customFileBlocks.length > 1) {
            selectBlocks[selectBlocks.length - qtd].remove();
            quantidadeBlocks[quantidadeBlocks.length - qtd].remove();
            customFileBlocks[customFileBlocks.length - qtd].remove();
            counter--;
        }

        if (selectBlocks.length <= 4 && quantidadeBlocks.length <= 4 && customFileBlocks.length <= 4) {
            remove.disabled = true;  // Disable the remove button if there's only one block left
        }
    }

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

    // Adicionando eventos de clique aos botões
    addButton.addEventListener('click', function () {
        let selectContainer = document.getElementById('selectContainerInspecao');
        adicionarCausa('inputNaoConformidadesSolda',selectContainer,addButton,'','tipos_causas_solda');
        removeButton.disabled = false;
    });
    removeButton.addEventListener('click', function () {
        removerCausa('tipos_causas_solda',removeButton,3)
    });
    addButtonReinspecao.addEventListener('click', function () {
        let selectContainerReinspecao = document.getElementById('selectContainerReinspecao');
        adicionarCausa('inputReinspecionadasNaoConformidadesSolda',selectContainerReinspecao,addButtonReinspecao,'R','tipos_causas_solda_reinspecao');
        removeButtonReinspecao.disabled = false;
    });
    removeButtonReinspecao.addEventListener('click', function () {
        removerCausa('tipos_causas_solda_reinspecao',removeButtonReinspecao,2)
    });
    addButtonSoldaEdicao.addEventListener('click', function () {
        let selectContainerReinspecao = document.getElementById('selectContainerEdicao');
        adicionarCausa('num_causas_edicao',selectContainerReinspecao,addButtonSoldaEdicao,'E','tipos_causas_solda_edicao');
        removeButtonSoldaEdicao.disabled = false;
    });
    removeButtonSoldaEdicao.addEventListener('click', function () {
        removerCausa('tipos_causas_solda_edicao',removeButtonSoldaEdicao,1)
    });

    let qtd_conformidade_edicao = document.getElementById("qtd_conformidade_edicao");
    let qtd_conformidade_atualizada_edicao = document.getElementById("qtd_conformidade_atualizada_edicao");
    let num_causas_edicao = document.getElementById("num_causas_edicao").value

    if (qtd_conformidade_atualizada_edicao) {
        qtd_conformidade_atualizada_edicao.addEventListener("input", () => {
            num_causas_edicao = parseInt(qtd_conformidade_edicao.value) - parseInt(qtd_conformidade_atualizada_edicao.value)
            if(parseInt(qtd_conformidade_atualizada_edicao.value) < 0 || parseInt(qtd_conformidade_atualizada_edicao) === ''){
                $("#coluna_causa_edicao_solda").empty()
                return
            }
            $('#num_causas_edicao').val(num_causas_edicao)
        });
    }
});
