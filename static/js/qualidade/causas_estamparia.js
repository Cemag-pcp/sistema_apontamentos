let selectCounter = 0; // Contador inicializado em 0

function adicionarCausa() {
    const original = document.getElementById('selectBlock');
    const clone = original.cloneNode(true);
    const newSelect = clone.getElementsByTagName('select')[0];
    
    selectCounter++;
    newSelect.id = `retrabalhoSolda${selectCounter}`;
    newSelect.name = `retrabalhoSolda${selectCounter}`;
    
    document.getElementById('selectContainer').appendChild(clone);
    updateRemoveButton();
}

function removerCausa() {
    const container = document.getElementById('selectContainer');
    if (container.children.length > 1) {
        container.removeChild(container.lastChild);
        selectCounter--;
        updateRemoveButton();
    }
}

function updateRemoveButton() {
    const removeButton = document.getElementById('removeButton');
    // Desativa o botão se houver apenas um 'select', caso contrário, reativa.
    if (document.getElementById('selectContainer').children.length <= 2) {
        removeButton.disabled = true;
    } else {
        removeButton.disabled = false;
    }
}

// Função para verificar o estado inicial do botão de remoção ao carregar a página.
window.onload = function() {
    updateRemoveButton();
}