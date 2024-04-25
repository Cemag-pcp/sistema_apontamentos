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
