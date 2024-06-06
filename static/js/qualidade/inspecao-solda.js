function modalInspecaoSolda(id_inspecao,categoria,conjunto,quantidade) {

    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);

    $('#inspecionarConjuntoLabel').text(id_inspecao)

    $("#inputCategoria").val(categoria);
    $("#inputConjunto").val(conjunto);
    $('#inputPecasProduzidas').val(quantidade);

    $("#inputPecasInspecionadasSolda").val('')
    $("#inputConformidadesSolda").val('')
    $("#inspetorSolda").val('')
    $("#observacaoSolda").val('')
    $("#causasSolda-0").val('')
    $("#quantidade_causas_solda-0").val('')
    $("#outraCausaSolda").val('')
    $("#inputNaoConformidadesSolda").val('')

    $("#causaSolda").prop('disabled',false);
    $("#outraCausaSolda").prop('disabled',true);

    $('#data_inspecao_solda').val(today.toLocaleDateString());

    $('#inspecionarConjunto').modal('show');

}

$('#inputConformidadesSolda').on('input', function(){
    
    let pecasInspecionadasSolda = $('#inputPecasInspecionadasSolda').val();
    let numConformidadesSolda = $('#inputConformidadesSolda').val();
    let numNaoConformidadesSolda = $('#inputNaoConformidadesSolda');
    let selectNaoConformidadesSolda = $("#selectNaoConformidadesSolda");
    let outroCausaSolda = $("#outraCausaSolda");
    let containerCausas = $("#selectContainerInspecao");
    let origemInspecaoSoldaReinspecionadas = $('#origemInspecaoCol');

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
        selectNaoConformidadesSolda.prop('disabled',true);
        containerCausas.css('display','none')
        outroCausaSolda.prop('disabled',true);
        selectNaoConformidadesSolda.val('')
        outroCausaSolda.val('')
        origemInspecaoSoldaReinspecionadas.css('display','none')
        origemInspecaoSoldaReinspecionadas.val(null)
    } else {
        outroCausaSolda.prop('disabled',false);
        containerCausas.css('display','flex')
        selectNaoConformidadesSolda.prop('disabled',false);
        origemInspecaoSoldaReinspecionadas.css('display','block')
    }

})

$('#inputPecasInspecionadasSolda').on('blur', function() {

    let inspecionados = $('#inputPecasInspecionadasSolda');
    let produzidas = parseInt($('#inputPecasProduzidas').val());
    let inputConformidadesSolda = $('#inputConformidadesSolda');
    let inputNaoConformidadesSolda = $('#inputNaoConformidadesSolda');

    if((inspecionados.val() > produzidas || inspecionados.val() <= 0) && inspecionados.val() != ''){
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
    let tipos_causas_solda = $('#tipos_causas_solda').val();
    let qtd_causas = 0

    if (inputConformidadesSolda === "" || inspetoresSolda === null || inputConformidadesSolda > inputPecasInspecionadasSolda || inputConformidadesSolda < 0) {
        alert('Verifique se o campo de conformidades está com valor correto');
        $("#loading").hide();
        return; // Interrompe a execução
    }

    for (var i = 0; i < tipos_causas_solda; i++) {
        qtd_causas += parseInt($("#quantidade_causas_solda-" + i).val())
        let causas = $("#causasSolda-" + i).val();
        if (causas === null && inputNaoConformidadesSolda != 0) {
            alert('Preencha todos os campos das causas de não conformidade.');
            $("#loading").hide();
            return; // Interrompe a execução
        }
    }

    if((qtd_causas != inputNaoConformidadesSolda) && inputNaoConformidadesSolda != 0){
        alert('Verifique se a soma dos campos de "Quantidade" está igual ao valor de "Total de NÃO conformidades"');
        $("#loading").hide();
        return; // Interrompe a execução
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
    let inputPecasInspecionadasSolda = parseInt($('#inputPecasInspecionadasSolda').val());
    let inputConformidadesSolda = parseInt($('#inputConformidadesSolda').val());
    let inputNaoConformidadesSolda = $('#inputNaoConformidadesSolda').val();
    let inspetorSolda = $('#inspetorSolda').val();
    let list_causas = [];
    let list_quantidade = [];
    let outraCausaSolda = $('#outraCausaSolda').val();
    let observacaoSolda = $('#observacaoSolda').val();
    let origemInspecaoSolda = $('#origemInspecaoSoldaReinspecionadas').val();
    let tipos_causas_solda = $('#tipos_causas_solda').val();
    let reinspecao = 'False';

    if (inputConformidadesSolda === "" || inputConformidadesSolda > inputPecasInspecionadasSolda || inputConformidadesSolda < 0) {
        alert('Verifique se o campo de conformidades está com valor correto');
        $('#btnEnviarSolda').prop('disabled',false);
        $("#loading").hide();
        return; // Interrompe a execução
    }

    for (var i = 0; i < tipos_causas_solda; i++) {
        let causas = $("#causasSolda-" + i).val();
        let quantidade = $("#quantidade_causas_solda-" + i).val();
        let inputId = '#inputGroupFile_solda-' + i;
        let files = $(inputId)[0].files;
        for (let file of files) {
            formData.append('foto_inspecao_' + i + '[]', file);
        }
        list_causas.push(causas)
        list_quantidade.push(quantidade)
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
    formData.append('list_quantidade', JSON.stringify(list_quantidade));
    formData.append('outraCausaSolda', outraCausaSolda);
    formData.append('observacaoSolda', observacaoSolda);
    formData.append('origemInspecaoSolda', origemInspecaoSolda);
    formData.append('tipos_causas_solda',tipos_causas_solda);
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