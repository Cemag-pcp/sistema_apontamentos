function modalInspecionarConjunto(id_inspecao,categoria,conjunto,quantidade) {

    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);

    $('#inspecionarConjuntoLabel').text(id_inspecao)

    $("#inputCategoria").val(categoria);
    $("#inputConjunto").val(conjunto);
    $('#inputPecasInspecionadasSolda').val(quantidade);

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
    let outroCausaSolda = $("#outraCausaSolda");
    let origemInspecaoSoldaReinspecionadas = $('#origemInspecaoCol');

    numNaoConformidadesSolda.val(pecasInspecionadasSolda - numConformidadesSolda);

    if(numConformidadesSolda === ''){
        numNaoConformidadesSolda.val('')
    } 

    if(numNaoConformidadesSolda.val() === '' || numNaoConformidadesSolda.val() <= 0 || numConformidadesSolda < 0){
        selectNaoConformidadesSolda.prop('disabled',true);
        outroCausaSolda.prop('disabled',true);
        selectNaoConformidadesSolda.val('')
        outroCausaSolda.val('')
        origemInspecaoSoldaReinspecionadas.css('display','none')
        origemInspecaoSoldaReinspecionadas.val(null)
    } else {
        outroCausaSolda.prop('disabled',false);
        selectNaoConformidadesSolda.prop('disabled',false);
        origemInspecaoSoldaReinspecionadas.css('display','block')
    }

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