document.addEventListener("DOMContentLoaded", function () {
    function setupDynamicFields(groupId) {
        const addButton = document.getElementById(`addButton${groupId}`);
        const removeButton = document.getElementById(`removeButton${groupId}`);
        const causasContainer = document.getElementById(`causasContainer${groupId}`);

        function updateFileLabel(inputElement) {
            const label = inputElement.nextElementSibling; // O próximo elemento é a label
            if (inputElement.files.length > 0) {
                label.textContent = `${inputElement.files.length} arquivo${inputElement.files.length > 1 ? 's' : ''}`;
            } else {
                label.textContent = "0 arquivos";
            }
        }

        causasContainer.addEventListener("change", function (event) {
            if (event.target.type === "file") {
                updateFileLabel(event.target);
            }
        });

        addButton.addEventListener("click", function () {
            // Clona o bloco original
            const originalBlock = causasContainer.querySelector(".causasBlock");
            const clonedBlock = originalBlock.cloneNode(true);

            // Reseta valores dos inputs no bloco clonado
            clonedBlock.querySelectorAll("select, input").forEach((element) => {
                if (element.type === "file") {
                    element.value = null;
                    const label = clonedBlock.querySelector(".custom-file-label");
                    if (label) label.textContent = "0 arquivos";
                } else {
                    element.value = "";
                }
            });

            // Adiciona o bloco clonado ao container
            causasContainer.appendChild(clonedBlock);

            // Habilita o botão de remoção
            removeButton.disabled = false;
        });

        removeButton.addEventListener("click", function () {
            // Remove o último bloco criado
            const blocks = causasContainer.querySelectorAll(".causasBlock");
            if (blocks.length > 1) {
                causasContainer.removeChild(blocks[blocks.length - 1]);
            }

            // Desabilita o botão de remoção se só sobrar o bloco original
            if (blocks.length <= 1) {
                removeButton.disabled = true;
            }
        });
    }

    // Configurar todos os grupos dinâmicos
    const dynamicGroups = ["Estanqueidade", "EstanqueidadeCilindro", "EstanqueidadeTubo"]; // IDs dos grupos
    dynamicGroups.forEach(setupDynamicFields);
});
