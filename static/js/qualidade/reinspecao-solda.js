
function modalReinspecaoSolda(id,data, n_nao_conformidades,conjunto,categoria) {

    // Configurar o conteúdo do modal com os parâmetros recebidos
    $('#reinspecionarConjuntoLabel').text(id)
    $('#data_reinspecao_solda').val(data);
    $('#inputPecasReinspecionadasSolda').val(n_nao_conformidades)
    $("#inputConjuntoReinspecao").val(conjunto);
    $("#categoria_reinspecao_solda").val(categoria);
    
    // Exibir o modal
    $('#reinspecaoModalSolda').modal('show');

}


$('#inputReinspecionadasConformidadesSolda').on('input',function() {

    let pecasInspecionadasSolda = $('#inputPecasReinspecionadasSolda').val();
    let numConformidadesSolda = $('#inputReinspecionadasConformidadesSolda').val();
    let numNaoConformidadesSolda = $('#inputReinspecionadasNaoConformidadesSolda');
    let selectNaoConformidadesSolda = $("#selectReinspecionadasNaoConformidadesSolda");
    let outraCausaSoldaReinspecionadas = $("#outraCausaSoldaReinspecionadas");

    numNaoConformidadesSolda.val(pecasInspecionadasSolda - numConformidadesSolda);

    if(numConformidadesSolda === ''){
        numNaoConformidadesSolda.val('')
    }

    if(numNaoConformidadesSolda.val() === '' || numNaoConformidadesSolda.val() <= 0 || numConformidadesSolda < 0){
        selectNaoConformidadesSolda.prop('disabled',true);
        outraCausaSoldaReinspecionadas.prop('disabled',true);
        selectNaoConformidadesSolda.val('')
        outraCausaSoldaReinspecionadas.val('')
    } else {
        selectNaoConformidadesSolda.prop('disabled',false);
        outraCausaSoldaReinspecionadas.prop('disabled',false);
        outraCausaSoldaReinspecionadas.val('')
    }

})


$('#envio_reinspecao_Solda').on('click',function() {
    let inputConformidadesSolda = $('#inputReinspecionadasConformidadesSolda').val();
    let inputNaoConformidadesSolda = $('#inputReinspecionadasNaoConformidadesSolda').val();
    let inputPecasInspecionadasSolda = parseInt($('#inputPecasReinspecionadasSolda').val());
    let inputConjunto = $('#inputConjuntoReinspecao').val();
    let observacaoSolda = $('#observacaoSoldaReinspecionadas').val();
    let inspetoresSolda = $('#inspetoresSoldaReinspecao').val();

    $("#confirmarConformidades").val(inputConformidadesSolda);
    $("#confirmarNaoConformidades").val(inputNaoConformidadesSolda);

    $('#modalConfirmacaoSolda #p_confirmar_inspecao_solda').text("Deseja confirmar as informações preenchidas referente a reinspeção do conjunto " + inputConjunto);

    $("#btnEnviarSoldaReinspecao").css("display","block")
    $("#btnEnviarSolda").css("display","none")

    if (inputConformidadesSolda === "" || inspetoresSolda === null || inputConformidadesSolda > inputPecasInspecionadasSolda || inputConformidadesSolda < 0) {
        alert('Verifique se o campo de conformidades está com valor correto');
        $("#loading").hide();
        return; // Interrompe a execução
    }

    if (observacaoSolda.trim() === "" ) {
        alert('Verifique se os campos de causa e observação estão com os valores corretos');
        $("#loading").hide();
        return; // Interrompe a execução
    }

    for (var i = 1; i <= inputNaoConformidadesSolda; i++) {
        let causas = $("#causa_reinspecao_" + i).val();
        if (causas === "") {
            alert('Por favor, preencha todos os campos de causas de não conformidade.');
            $('#btnEnviarSoldaReinspecao').prop('disabled',false);
            $("#loading").hide();
            return; // Interrompe a execução
        }
    }

    $('#reinspecaoModalSolda').modal('hide');

    $('#modalConfirmacaoSolda').modal('show');
})

$('#btnEnviarSoldaReinspecao').on('click',function() {

    $("#loading").show();

    var formData = new FormData();

    $('#btnEnviarSoldaReinspecao').prop('disabled',true);

    let id_inspecao = $('#reinspecionarConjuntoLabel').text();
    let data_inspecao = $('#data_reinspecao_solda').val();
    let inputCategoria = $('#categoria_reinspecao_solda').val();
    let inputConjunto = $('#inputConjuntoReinspecao').val();
    let inputPecasInspecionadasSolda = parseInt($('#inputPecasReinspecionadasSolda').val());
    let inputConformidadesSolda = parseInt($('#inputReinspecionadasConformidadesSolda').val());
    let inputNaoConformidadesSolda = parseInt($('#inputReinspecionadasNaoConformidadesSolda').val());
    let inspetoresSolda = $('#inspetoresSoldaReinspecao').val();
    let retrabalhoSolda = [];
    let list_causas = [];
    let outraCausaSolda = $('#outraCausaSoldaReinspecionadas').val();
    let observacaoSolda = $('#observacaoSoldaReinspecionadas').val();
    let origemInspecaoSolda = $('#origemSoldaReinspecionadas').val();
    let reinspecao = "True";
   
    $('select[id^="retrabalhoSolda"]').each(function() {
        if($(this).val() !== null){
            retrabalhoSolda.push($(this).val()); // Adiciona o valor de cada select à lista
        } 
    });

    for (var i = 1; i <= inputNaoConformidadesSolda; i++) {
        let causas = $("#causa_reinspecao_" + i).val();
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
    formData.append('inspetorSolda', inspetoresSolda);
    formData.append('num_pecas', inputPecasInspecionadasSolda);
    formData.append('inputConformidadesSolda', inputConformidadesSolda);
    formData.append('inputNaoConformidadesSolda', inputNaoConformidadesSolda);
    formData.append('list_causas', JSON.stringify(list_causas));
    formData.append('retrabalhoSolda', JSON.stringify(retrabalhoSolda));
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
            $('#btnEnviarSoldaReinspecao').prop('disabled',false);
        }
    });

})