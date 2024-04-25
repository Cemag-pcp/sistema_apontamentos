var id_inspecao_solda;

function modalReinspecaoSolda(id,data, n_nao_conformidades, causa_reinspecao,inspetor,conjunto,tipo_nao_conformidade,outra_causa,origem,observacao) {

    console.log(tipo_nao_conformidade)
    id_inspecao_solda = id;
    // Configurar o conteúdo do modal com os parâmetros recebidos
    $('#data_reinspecao_solda').val(data);
    $('#inputPecasReinspecionadasSolda').val(n_nao_conformidades)
    $("#causaSoldaReinspecionadas").val(causa_reinspecao)
    $('#inspetorSoldaReinspecao').val(inspetor);
    $("#inputConjuntoReinspecao").val(conjunto);
    $('#selectReinspecionadasNaoConformidadesSolda').val(tipo_nao_conformidade);
    $('#outraCausaSoldaReinspecionadas').val(outra_causa);
    $('#origemInspecaoSoldaReinspecionadas').val(origem);
    $('#observacaoSoldaReinspecionadas').val(observacao);
    
    // Exibir o modal
    $('#reinspecaoModalSolda').modal('show');

}


$('#inputReinspecionadasConformidadesSolda').on('input',function() {

    let pecasInspecionadasSolda = $('#inputPecasReinspecionadasSolda').val();
    let numConformidadesSolda = $('#inputReinspecionadasConformidadesSolda').val();
    let numNaoConformidadesSolda = $('#inputReinspecionadasNaoConformidadesSolda');
    let selectNaoConformidadesSolda = $("#selectReinspecionadasNaoConformidadesSolda");
    let causaSolda = $("#causaSoldaReinspecionadas");

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

$("#causaSoldaReinspecionadas").on('change',function(){

    if($("#causaSoldaReinspecionadas").val() === "Outro"){
        $('#outraCausaSoldaReinspecionadas').prop('disabled',false)
    } else {
        $('#outraCausaSoldaReinspecionadas').prop('disabled',true)
        $('#outraCausaSoldaReinspecionadas').val('')
    }
})


$('#envio_reinspecao_Solda').on('click',function() {

    $('#loading').show();

    let pecasInspecionadasSolda = $('#inputPecasReinspecionadasSolda').val();
    let numConformidadesSolda = $('#inputReinspecionadasConformidadesSolda').val();

    let inputNaoObrigatorio = $("#reinspecaoModalSolda input:not(.desabilitado)");
    let selectNaoObrigatorio = $("#reinspecaoModalSolda select:not(.desabilitado)");
    let textareaNaoObrigatorio = $("#reinspecaoModalSolda textarea:not(.desabilitado)");

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
        $('#inputReinspecionadasConformidadesSolda').val('')
        $('#inputReinspecionadasNaoConformidadesSolda').val('')
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
        data: JSON.stringify({ 'id_inspecao_solda':id_inspecao_solda,'data_inspecao': $('#data_reinspecao_solda').val(),'inspetor': $('#inspetorSoldaReinspecao').val(), 'conjunto_especifico': $('#inputConjuntoReinspecao').val(),
        'num_pecas': $('#inputPecasReinspecionadasSolda').val(),'num_conformidades': $('#inputReinspecionadasConformidadesSolda').val(),
        'num_nao_conformidades': $('#inputReinspecionadasNaoConformidadesSolda').val(), 'tipo_nao_conformidade': $('#selectReinspecionadasNaoConformidadesSolda').val(),'causaSolda': $('#causaSoldaReinspecionadas').val(),
        'outraCausaSolda': $('#outraCausaSoldaReinspecionadas').val(),'origemInspecaoSolda': $('#origemInspecaoSoldaReinspecionadas').val(),'observacaoSolda': $('#observacaoSoldaReinspecionadas').val(), 'modal_reinspecao_solda' : true}), // Enviando um objeto JSON
        success: function(response) {
            console.log(response);
            window.location.reload();
            $('#loading').hide();
        },
        error: function(error) {
            console.log(error);
            $('#loading').hide();
        }
    });

})