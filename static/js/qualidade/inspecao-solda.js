function modalInspecionarConjunto() {

    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);

    $("#inspecionarConjunto input").val('');
    $("#inspecionarConjunto select").val('');
    $("#inspecionarConjunto textarea").val('');
    $("#selectNaoConformidadesSolda").prop('disabled',false);
    $("#causaSolda").prop('disabled',false);
    $("#outraCausaSolda").prop('disabled',true);

    $('#data_inspecao_solda').val(today.toLocaleDateString());

    $('#inspecionarConjunto').modal('show');

}

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

$('#inputConformidadesSolda').on('input',function(){
    let pecasInspecionadasSolda = $('#inputPecasInspecionadasSolda').val();
    let numConformidadesSolda = $('#inputConformidadesSolda').val();
    let numNaoConformidadesSolda = $('#inputNaoConformidadesSolda');
    let selectNaoConformidadesSolda = $("#selectNaoConformidadesSolda");
    let causaSolda = $("#causaSolda");

    numNaoConformidadesSolda.val(pecasInspecionadasSolda - numConformidadesSolda);

    if(numConformidadesSolda === ''){
        numNaoConformidadesSolda.val('')
    }

    if(numNaoConformidadesSolda.val() === '' || numNaoConformidadesSolda.val() <= 0 || numConformidadesSolda < 0){
        selectNaoConformidadesSolda.prop('disabled',true);
        causaSolda.prop('disabled',true);
        $('#outraCausaSolda').prop('disabled',true)
        selectNaoConformidadesSolda.val('')
        causaSolda.val('')
        $('#outraCausaSolda').val('')
    } else {
        selectNaoConformidadesSolda.prop('disabled',false);
        causaSolda.prop('disabled',false);
        $('#outraCausaSolda').val('')
    }

})

$('#inputPecasInspecionadasSolda').on('input',function(){
    let pecasInspecionadasSolda = $('#inputPecasInspecionadasSolda').val();
    let numConformidadesSolda = $('#inputConformidadesSolda').val();
    let numNaoConformidadesSolda = $('#inputNaoConformidadesSolda');
    let selectNaoConformidadesSolda = $("#selectNaoConformidadesSolda");
    let causaSolda = $("#causaSolda");

    numNaoConformidadesSolda.val(pecasInspecionadasSolda - numConformidadesSolda);

    if(numConformidadesSolda === ''){
        numNaoConformidadesSolda.val('')
    }

    if(numNaoConformidadesSolda.val() === '' || numNaoConformidadesSolda.val() <= 0 || numConformidadesSolda < 0){
        selectNaoConformidadesSolda.prop('disabled',true);
        causaSolda.prop('disabled',true);
        $('#outraCausaSolda').prop('disabled',true)
        selectNaoConformidadesSolda.val('')
        causaSolda.val('')
        $('#outraCausaSolda').val('')
    } else {
        selectNaoConformidadesSolda.prop('disabled',false);
        causaSolda.prop('disabled',false);
        $('#outraCausaSolda').val('')
    }

})

$("#causaSolda").on('change',function(){

    if($("#causaSolda").val() === "Outro"){
        $('#outraCausaSolda').prop('disabled',false)
    } else {
        $('#outraCausaSolda').prop('disabled',true)
        $('#outraCausaSolda').val('')
    }
})


$('#envio_inspecao_solda').on('click',function() {

    $('#loading').show();

    let pecasInspecionadasSolda = $('#inputPecasInspecionadasSolda').val();
    let numConformidadesSolda = $('#inputConformidadesSolda').val();

    let inputNaoObrigatorio = $("#inspecionarConjunto input:not(.desabilitado)");
    let selectNaoObrigatorio = $("#inspecionarConjunto select:not(.desabilitado)");
    let textareaNaoObrigatorio = $("#inspecionarConjunto textarea:not(.desabilitado)");
    

    console.log(selectNaoObrigatorio)

    let inputsVazios = inputNaoObrigatorio.filter(function() {
        return $(this).val().trim() === ''; // Verifica se o valor do input está vazio
    });
    
    let selectsVazios = selectNaoObrigatorio.filter(function() {
        return $(this).val() === ''; // Verifica se o valor do select está vazio
    });
    
    let textareasVazias = textareaNaoObrigatorio.filter(function() {
        return $(this).val().trim() === ''; // Verifica se o valor do textarea está vazio
    });

    if(pecasInspecionadasSolda < numConformidadesSolda || numConformidadesSolda < 0) {
        alert("Preencha os campos corretamente. Verifique se número de conformidades maior que número de peças ou se possui valores vazios referente a peças ou N° Conformidade")
        $('#inputConformidadesSolda').val('')
        $('#inputNaoConformidadesSolda').val('')
        $('#loading').hide();
        return;
    } 

    if(inputsVazios.length > 0 || selectsVazios.length > 0 || textareasVazias.length > 0){
        alert("Preencha todos os campos.")
        $('#loading').hide();
        return;
    }

    $.ajax({
        url: '/inspecao-solda',
        type: 'POST',  // Alterado para POST
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({ 'data_inspecao': $('#data_inspecao_solda').val(),'inspetor': $('#inspetorSolda').val(),'conjunto_especifico': $('#inputConjunto').val(),
        'num_pecas': $('#inputPecasInspecionadasSolda').val(),'num_conformidades': $('#inputConformidadesSolda').val(),
        'num_nao_conformidades': $('#inputNaoConformidadesSolda').val(), 'tipo_nao_conformidade': $('#selectNaoConformidadesSolda').val(),'causaSolda': $('#causaSolda').val(),'outraCausaSolda': $('#outraCausaSolda').val(),
        'origemInspecaoSolda': $('#origemInspecaoSolda').val(),'observacaoSolda': $('#observacaoSolda').val(), 'modal_reinspecao_solda' : false}), // Enviando um objeto JSON
        success: function(response) {
            console.log(response);
            window.location.reload();
            $('#loading').hide();
        },
        error: function(error) {
            console.log(error);
            window.location.reload();
            $('#loading').hide();
        }
    });

})
