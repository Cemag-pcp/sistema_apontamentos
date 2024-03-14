// Populando lista de operadores
function carregarConjuntos(conjuntos) {

    $('#loading').show()

    var inputConjunto = $("#inputConjunto")
    inputConjunto.val('')
    var listConjunto = document.getElementById('listConjunto');

    // Caso contrário, faz a solicitação AJAX

    $.ajax({
        url: '/conjuntos',
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({ 'conjuntos': conjuntos }),
        success: function (data) {
            atualizarLista(data);
            $('#loading').hide()
        }
    });

    function atualizarLista(conjuntos) {
        listConjunto.innerHTML = '';

        conjuntos.forEach(function (conjunto) {
            var li = document.createElement('li');
            li.textContent = conjunto;
            listConjunto.appendChild(li);
        });
    }
}
var selectConjunto = $('#selectConjunto');
// Adiciona eventos tanto para o clique quanto para o foco
selectConjunto.on('change',function(){
    carregarConjuntos(selectConjunto.val())
})
// Fim Populando lista de operadores

// Criar listas dentro do input
function configurarDropdown(inputId, listId) {
    var inputDropdown = document.getElementById(inputId);
    var listaDropdown = document.getElementById(listId);
    var itens = listaDropdown.getElementsByTagName('li');
    var valorAnterior = "";

    inputDropdown.addEventListener('focus', function () {
        if (inputDropdown.readOnly) {
            listaDropdown.style.display = 'none';
        } else {
            listaDropdown.style.display = 'block';
        }
    });

    inputDropdown.addEventListener('blur', function () {
        // Aguarde um curto período antes de ocultar a lista para permitir que o clique no item seja processado
        setTimeout(function () {
            if (!correspondeAItem()) {
                // Se o valor não corresponder a um item na lista, redefina para o valor anterior
                inputDropdown.value = valorAnterior;
            }
            listaDropdown.style.display = 'none';
        }, 200);
    });

    listaDropdown.addEventListener('click', function (event) {
        if (event.target.tagName === 'LI') {
            valorAnterior = event.target.textContent;
            inputDropdown.value = valorAnterior;

            // Oculte a lista após um pequeno atraso para garantir que o valor do input seja atualizado antes
            setTimeout(function () {
                listaDropdown.style.display = 'none';
            }, 100);
        }
    });

    inputDropdown.addEventListener('input', function () {
        var input = this.value.trim().toLowerCase();
        var itens = listaDropdown.getElementsByTagName('li');

        for (var i = 0; i < itens.length; i++) {
            var textoItem = itens[i].textContent.toLowerCase();
            var itemVisivel = textoItem.indexOf(input) > -1;
            itens[i].style.display = itemVisivel ? 'block' : 'none';
        }

        // Exiba a lista apenas se houver correspondência com os itens
        var correspondenciaItens = Array.from(itens).some(function (item) {
            var textoItem = item.textContent.toLowerCase();
            var itemVisivel = textoItem.includes(input);
            item.style.display = itemVisivel ? 'block' : 'none';
            return itemVisivel;
        });

        listaDropdown.style.display = correspondenciaItens ? 'block' : 'none';
    });

    function correspondeAItem() {
        var input = inputDropdown.value.trim().toLowerCase();
        return Array.from(itens).some(function (item) {
            return item.textContent.toLowerCase() === input;
        });
    }
}

configurarDropdown('inputConjunto', 'listConjunto');
// Fim criar lista dentro de input

function modalInspecionarConjunto() {

    $("#inspecionarConjunto input").val('');
    $("#inspecionarConjunto select").val('');
    $("#inspecionarConjunto textarea").val('');

    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);

    $('#data_inspecao_solda').val(today.toLocaleDateString());

    $('#inspecionarConjunto').modal('show');

}

$('#inputConformidadesSolda').on('input',function(){
    let pecasInspecionadasSolda = $('#inputPecasInspecionadasSolda').val();
    let numConformidadesSolda = $('#inputConformidadesSolda').val();
    let numNaoConformidadesSolda = $('#inputNaoConformidadesSolda');

    numNaoConformidadesSolda.val(pecasInspecionadasSolda - numConformidadesSolda);

})

$('#envio_inspecao_solda').on('click',function() {
    let pecasInspecionadasSolda = $('#inputPecasInspecionadasSolda').val();
    let numConformidadesSolda = $('#inputConformidadesSolda').val();

    if(pecasInspecionadasSolda < numConformidadesSolda || numConformidadesSolda < 0) {
        alert("Preencha os campos corretamente. Verifique se número de conformidades maior que número de peças ou se possui valores vazios referente a peças ou N° Conformidade")
        $('#inputConformidadesSolda').val('')
        $('#inputNaoConformidadesSolda').val('')
        return;
    }
})
