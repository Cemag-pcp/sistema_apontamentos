document.addEventListener('DOMContentLoaded', function () {
    function updatePieceNumbers() {
        const blocks = document.querySelectorAll('.campo_dinamico');
        blocks.forEach((block, index) => {
            const pieceNumber = index + 1;
            block.querySelector('h6').textContent = `Peça ${pieceNumber}`;
            block.querySelectorAll('input, select').forEach(element => {
                const idPrefix = element.id.replace(/\d+$/, '');
                element.id = `${idPrefix}${pieceNumber}`;
                const namePrefix = element.name.replace(/\d+$/, '');
                element.name = `${namePrefix}${pieceNumber}`;
            });
        });
    }

    document.getElementById('adicionar-peca').addEventListener('click', function () {
        // Incrementa o contador global
        const blocks = document.querySelectorAll('.campo_dinamico');
        const pieceCount = blocks.length + 1;

        // Cria um novo bloco dinâmico
        const newBlock = document.createElement('div');
        newBlock.className = 'campo_dinamico';
        newBlock.innerHTML = `
            <hr>
            <h6 class="mb-3 font-weight-bold text-primary">Peça ${pieceCount}</h6>
            <hr>
            <div class="row">
                <div class="col-sm-5 mb-4">
                    <div class="form-floating mb-3">
                        <label for="userInput_${pieceCount}">Peça</label>
                        <div class="position-relative">
                            <input class="form-control" type="text" id="userInput_${pieceCount}" oninput="showSuggestionsPecas('userInput_${pieceCount}', 'suggestionsPecas_${pieceCount}','peca-modal_${pieceCount}')">
                            <span id="peca-modal_${pieceCount}" class="clear-icon-operador" onclick="clearInput('userInput_${pieceCount}', 'suggestionsPecas_${pieceCount}')">x</span>
                            <ul id="suggestionsPecas_${pieceCount}" class="custom-dropdown-menu" style="display: none;"></ul>
                        </div>
                    </div>
                </div>
                <div class="col-sm-2 mb-4">
                    <div class="form-floating mb-3">
                        <label for="inputQuantidade_${pieceCount}">Quantidade</label>
                        <input class="form-control" type="number" id="inputQuantidade_${pieceCount}">
                    </div>
                </div>
                <div class="col-sm-3 mb-4">
                    <label for="maquinaForaDoPlanejado_${pieceCount}">Máquina</label>
                    <div class="position-relative">
                        <select id="maquinaForaDoPlanejado_${pieceCount}" name="maquinaForaDoPlanejado_${pieceCount}" class="form-control">
                            <option value="" disabled selected>Selecione uma máquina</option>
                            <option value="Viradeira 1">Viradeira 1</option>
                            <option value="Viradeira 2">Viradeira 2</option>
                            <option value="Viradeira 3">Viradeira 3</option>
                            <option value="Viradeira 4">Viradeira 4</option>
                            <option value="Viradeira 5">Viradeira 5</option>
                            <option value="Prensa">Prensa</option>
                        </select>
                    </div>
                </div>
                <div class="col-sm-2 mb-4 d-flex align-items-center mt-3">
                    <button type="button" class="btn btn-danger btn-remover"><i class="fa-solid fa-trash"></i></button>
                </div>
            </div>
        `;

        // Adiciona o novo bloco ao container
        document.getElementById('campo_dinamico_container').appendChild(newBlock);
        updatePieceNumbers(); // Atualiza a numeração após adicionar
    });

    // Delegação de eventos para remover blocos
    document.getElementById('campo_dinamico_container').addEventListener('click', function (event) {
        if (event.target.closest('.btn-remover')) {
            event.target.closest('.campo_dinamico').remove();
            updatePieceNumbers();
        }
    });

    // Atualiza a numeração ao carregar a página
    updatePieceNumbers();
});

let suggestionsDataPecaModal = [];

// Função para mostrar sugestões ao digitar
function showSuggestionsPecas(inputId, suggestionsId,pecaModalId) {

    var input = $(`#${inputId}`).val().toLowerCase();

    var suggestionsList = $(`#${suggestionsId}`);
    var pecaModal = $(`#${pecaModalId}`);
    suggestionsList.empty(); // Limpa a lista de sugestões

    $(`#${suggestionsId}`).on('click', 'li', function () {
        $(`#${inputId}`).val($(this).text());
        $(`#${suggestionsId}`).hide();
    });

    // Evento de clique no ícone de limpar para limpar o campo de entrada e esconder a lista de sugestões
    pecaModal.click(function (event) {
        event.stopPropagation(); // Impede a propagação do evento para não ser capturado pelo document click
        clearInput(inputId,suggestionsId);
    });

    const filteredSuggestions = suggestionsDataPecaModal.filter(suggestion =>
        suggestion.toLowerCase().includes(input)
    );

    // Preenche a lista de sugestões com os itens filtrados
    filteredSuggestions.forEach(suggestion => {
        const li = $('<li>');
        const a = $('<a>').attr('href', '#').text(suggestion);
        a.on('click', function (event) {
            event.preventDefault();
            // Ação ao selecionar uma sugestão (pode ser ajustada conforme necessário)
            $(`#${inputId}`).val(suggestion);
            suggestionsList.css('display', 'none');
        });
        li.append(a);
        suggestionsList.append(li);
    });

    // Mostra a lista de sugestões
    suggestionsList.css('display', filteredSuggestions.length ? 'block' : 'none');

}

function clearInput(inputId,suggestionsId) {
    $(`#${inputId}`).val('');
    $(`#${suggestionsId}`).hide();
}

$(document).ready(function () {
    fetchSuggestion();
});

function fetchSuggestion() {
    $.ajax({
        url: '/sugestao-pecas-estamparia',
        method: 'GET',
        success: function (data) {
            suggestionsDataPecaModal = data.map(row => row[Object.keys(row)[0]]);
        },
        error: function (err) {
            console.error('Erro ao obter dados brutos do backend', err);
        }
    });
}

function validateInput(inputId) {
    const inputValue = $(`#${inputId}`).val();
    const isValid = suggestionsDataPecaModal.some(suggestion => suggestion.toLowerCase() === inputValue.toLowerCase());

    if (!isValid) {
        return false;
    }

    return true;
}