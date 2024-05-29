function modalInspecaoEstamparia(id_inspecao,maquina,conjunto,quantidade) {

    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);

    $('#inspecionarEstampariaLabel').text(id_inspecao)

    $("#inputMaquina_estamparia").val(maquina);
    $("#inputConjunto_estamparia").val(conjunto);
    $('#inputPecasProduzidas_estamparia').val(quantidade);

    $("#causa_estamparia").prop('disabled',false);
    $("#outraCausa_estamparia").prop('disabled',true);

    $('#data_inspecao_estamparia').val(today.toLocaleDateString());

    $('#inspecionarEstamparia').modal('show');

}

$('#inputConformidades_estamparia').on('input', function(){
    
    let pecasInspecionadasSolda = $('#inputPecasInspecionadas_estamparia').val();
    let numConformidadesSolda = $('#inputConformidades_estamparia').val();
    let numNaoConformidadesSolda = $('#inputNaoConformidades_estamparia');
    let outroCausaSolda = $("#outraCausa_estamparia");
    let origemInspecaoSoldaReinspecionadas = $('#origemInspecaoCol_estamparia');

    numNaoConformidadesSolda.val(pecasInspecionadasSolda - numConformidadesSolda);

    if(pecasInspecionadasSolda === ''){
        alert("Preencha o número de peças inspecionadas")
        $('#inputConformidadesSolda').val('')
        numNaoConformidadesSolda.val('')
        return
    } 

    if(numConformidadesSolda === ''){
        numNaoConformidadesSolda.val('')
    } 

    if(numNaoConformidadesSolda.val() === '' || numNaoConformidadesSolda.val() <= 0 || numConformidadesSolda < 0){
        outroCausaSolda.prop('disabled',true);
        outroCausaSolda.val('')
        origemInspecaoSoldaReinspecionadas.css('display','none')
        origemInspecaoSoldaReinspecionadas.val(null)
    } else {
        outroCausaSolda.prop('disabled',false);
        origemInspecaoSoldaReinspecionadas.css('display','block')
    }

})

$('#inputPecasInspecionadas_estamparia').on('blur', function() {

    let inspecionados = $('#inputPecasInspecionadas_estamparia');
    let produzidas = parseInt($('#inputPecasProduzidas_estamparia').val());
    let inputConformidadesSolda = $('#inputConformidades_estamparia');
    let inputNaoConformidadesSolda = $('#inputNaoConformidades_estamparia');

    if(inspecionados.val() > produzidas || inspecionados.val() <= 0){
        alert("Preencha a quantidade correta para o número de peças produzidas")
        inspecionados.val('')
    }
    inputConformidadesSolda.val('')
    inputNaoConformidadesSolda.val('')
})

$('#envio_inspecao_solda').on('click',function() {

    let inputConformidadesSolda = parseInt($('#inputConformidadesSolda').val());
    let inputNaoConformidadesSolda = parseInt($('#inputNaoConformidadesSolda').val());
    let inputConjunto = $('#inputConjunto').val();
    let inputPecasInspecionadasSolda = parseInt($('#inputPecasInspecionadasSolda').val());
    let observacaoSolda = $('#observacaoSolda').val();
    let inspetoresSolda = $('#inspetorSolda').val();

    if (inputConformidadesSolda === "" || inspetoresSolda === null || inputConformidadesSolda > inputPecasInspecionadasSolda || inputConformidadesSolda < 0) {
        alert('Verifique se o campo de conformidades está com valor correto');
        $("#loading").hide();
        return; // Interrompe a execução
    }

    for (var i = 1; i <= inputNaoConformidadesSolda; i++) {
        let causas = $("#causa_reinspecao_" + i).val();
        if (causas === "") {
            alert('Preencha todos os campos das causas de não conformidade.');
            $("#loading").hide();
            return; // Interrompe a execução
        }
    }

    if (observacaoSolda.trim() === "" ) {
        alert('Verifique se os campos de causa e observação estão com os valores corretos');
        $("#loading").hide();
        return; // Interrompe a execução
    }

    $("#confirmarConformidades").val(inputConformidadesSolda);
    $("#confirmarNaoConformidades").val(inputNaoConformidadesSolda);
    
    $('#modalConfirmacaoSolda #p_confirmar_inspecao_solda').text("Deseja confirmar as informações preenchidas referente a inspeção do conjunto " + inputConjunto);

    $("#btnEnviarSoldaReinspecao").css("display","none")
    $("#btnEnviarSolda").css("display","block")

    $('#inspecionarConjunto').modal('hide');

    $('#modalConfirmacaoSolda').modal('show');
})

$('#btnEnviarSolda').on('click',function() {

    $("#loading").show();

    var formData = new FormData();

    $('#btnEnviarSolda').prop('disabled',true);

    let id_inspecao = $('#inspecionarConjuntoLabel').text();
    let data_inspecao = $('#data_inspecao_solda').val();
    let inputCategoria = $('#inputCategoria').val();
    let inputConjunto = $('#inputConjunto').val();
    let inputPecasInspecionadasSolda = $('#inputPecasInspecionadasSolda').val();
    let inputConformidadesSolda = $('#inputConformidadesSolda').val();
    let inputNaoConformidadesSolda = $('#inputNaoConformidadesSolda').val();
    let inspetorSolda = $('#inspetorSolda').val();
    let list_causas = [];
    let outraCausaSolda = $('#outraCausaSolda').val();
    let observacaoSolda = $('#observacaoSolda').val();
    let origemInspecaoSolda = $('#origemInspecaoSoldaReinspecionadas').val();
    let reinspecao = 'False';

    if (inputConformidadesSolda.trim() === "" || inputConformidadesSolda.trim() > inputPecasInspecionadasSolda || inputConformidadesSolda.trim() < 0) {
        alert('Verifique se o campo de conformidades está com valor correto');
        $('#btnEnviarSolda').prop('disabled',false);
        $("#loading").hide();
        return; // Interrompe a execução
    }

    for (var i = 1; i <= inputNaoConformidadesSolda; i++) {
        let causas = $("#causa_reinspecao_" + i).val();
        if (causas.trim() === "") {
            alert('Preencha todos os campos das causas de não conformidade.');
            $('#btnEnviarSolda').prop('disabled',false);
            $("#loading").hide();
            return; // Interrompe a execução
        }
        list_causas.push(causas);
    }

    for (let i = 1; i <= inputNaoConformidadesSolda; i++) {
        let inputId = '#foto_inspecao_' + i;
        let files = $(inputId)[0].files;
        for (let file of files) {
            formData.append('foto_inspecao_' + i + '[]', file);
        }
    }

    formData.append('id_inspecao', id_inspecao);
    formData.append('data_inspecao', data_inspecao);
    formData.append('inputCategoria', inputCategoria);
    formData.append('inputConjunto', inputConjunto);
    formData.append('inspetorSolda', inspetorSolda);
    formData.append('num_pecas', inputPecasInspecionadasSolda);
    formData.append('inputConformidadesSolda', inputConformidadesSolda);
    formData.append('inputNaoConformidadesSolda', inputNaoConformidadesSolda);
    formData.append('list_causas', JSON.stringify(list_causas));
    formData.append('outraCausaSolda', outraCausaSolda);
    formData.append('observacaoSolda', observacaoSolda);
    formData.append('origemInspecaoSolda', origemInspecaoSolda);
    formData.append('reinspecao', reinspecao);

    $.ajax({
        url: '/inspecao-solda',
        type: 'POST',
        data: formData,
        processData: false, // Não processe os dados
        contentType: false, // Não defina o tipo de conteúdo
        success: function (response) {
            location.reload();
            console.log(response);
        },
        error: function (error) {
            $("#loading").hide();
            console.log(error);
            $('#btnEnviarSolda').prop('disabled',false);
        }
    });

})