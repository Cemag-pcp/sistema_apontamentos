function modalInspecaoEstamparia(id_inspecao,maquina,conjunto,quantidade) {

    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);

    $('#inspecionarEstampariaLabel').text(id_inspecao)

    $("#inputMaquina_estamparia").val(maquina);
    $("#inputConjunto_estamparia").val(conjunto);
    $('#inputPecasProduzidas_estamparia').val(quantidade);

    $("#causa_estamparia").prop('disabled',false);
    $("#outraCausa_estamparia").prop('disabled',true);
    $("#causasEstamparia-0").val('')
    $("#quantidade_causas_estamparia-0").val('')

    $('#data_inspecao_estamparia').val(today.toLocaleDateString());

    $('#inspecionarEstamparia').modal('show');

}

$('#inputConformidades_estamparia').on('blur', function() {
    let pecasInspecionadasSolda = parseInt($('#inputPecasInspecionadas_estamparia').val());
    let numConformidadesSolda = parseInt($('#inputConformidades_estamparia').val());
    let numNaoConformidadesSolda = $('#inputNaoConformidades_estamparia');

    if(numConformidadesSolda > pecasInspecionadasSolda || numNaoConformidadesSolda.val() > pecasInspecionadasSolda || numConformidadesSolda < 0){
        alert("Preencha o número de peças inspecionadas")
        $('#inputConformidades_estamparia').val('')
        numNaoConformidadesSolda.val('')
        return
    } 
})

$('#inputConformidades_estamparia').on('input', function() {
    
    let pecasInspecionadasSolda = $('#inputPecasInspecionadas_estamparia').val();
    let numConformidadesSolda = parseInt($('#inputConformidades_estamparia').val());
    let numNaoConformidadesSolda = $('#inputNaoConformidades_estamparia');
    let outroCausaSolda = $("#outraCausa_estamparia");
    let containerCausas = $("#selectContainer");
    let origemInspecaoSoldaReinspecionadas = $('#origemInspecaoCol_estamparia');

    numNaoConformidadesSolda.val(pecasInspecionadasSolda - numConformidadesSolda);

    if(pecasInspecionadasSolda === ''){
        alert("Preencha o número de peças inspecionadas")
        $('#inputConformidades_estamparia').val('')
        numNaoConformidadesSolda.val('')
        return
    } 

    if(numConformidadesSolda === ''){
        numNaoConformidadesSolda.val('')
    } 

    if(numNaoConformidadesSolda.val() === '' || numNaoConformidadesSolda.val() <= 0 || numConformidadesSolda < 0){
        outroCausaSolda.prop('disabled',true);
        containerCausas.css('display','none')
        $("#causasEstamparia-0").val('')
        $("#quantidade_causas_estamparia-0").val('')
        outroCausaSolda.val('')
        origemInspecaoSoldaReinspecionadas.css('display','none')
        origemInspecaoSoldaReinspecionadas.val(null)
    } else {
        outroCausaSolda.prop('disabled',false);
        containerCausas.css('display','flex')
        origemInspecaoSoldaReinspecionadas.css('display','block')
    }

})

$('#inputPecasInspecionadas_estamparia').on('blur', function() {

    let inspecionados = $('#inputPecasInspecionadas_estamparia');
    let produzidas = parseInt($('#inputPecasProduzidas_estamparia').val());
    let inputConformidadesSolda = $('#inputConformidades_estamparia');
    let inputNaoConformidadesSolda = $('#inputNaoConformidades_estamparia');

    if((inspecionados.val() > produzidas || inspecionados.val() <= 0) && inspecionados.val() != ''){
        alert("Preencha a quantidade correta para o número de peças produzidas")
        inspecionados.val('')
    }
    inputConformidadesSolda.val('')
    inputNaoConformidadesSolda.val('')
})

$('#envio_inspecao_estamparia').on('click',function() {

    let inputConformidadesSolda = parseInt($('#inputConformidades_estamparia').val());
    let inputNaoConformidadesSolda = parseInt($('#inputNaoConformidades_estamparia').val());
    let inputConjunto = $('#inputConjunto_estamparia').val();
    let inputPecasInspecionadasSolda = parseInt($('#inputPecasProduzidas_estamparia').val());
    let observacaoSolda = $('#observacao_estamparia').val();
    let inspetoresSolda = $('#inspetor_estamparia').val();
    let tipos_causas_estamparia = $("#tipos_causas_estamparia").val();
    let origemInspecaoSolda = $('#origemInspecao_estamparia').val();
    let qtd_causas = 0

    for (let i = 0; i < tipos_causas_estamparia; i++) {
        qtd_causas += parseInt($("#quantidade_causas_estamparia-" + i).val())
    }

    if((qtd_causas != inputNaoConformidadesSolda) && inputNaoConformidadesSolda != 0){
        alert('Verifique se a soma dos campos de "Quantidade" está igual ao valor de "Total de NÃO conformidades"');
        $("#loading").hide();
        return; // Interrompe a execução
    }

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

    $("#confirmarConformidades_estamparia").val(inputConformidadesSolda);
    $("#confirmarNaoConformidades_estamparia").val(inputNaoConformidadesSolda);
    
    $('#modalConfirmacaoEstamparia #p_confirmar_inspecao_estamparia').text("Deseja confirmar as informações preenchidas referente a inspeção do conjunto " + inputConjunto);

    $("#btnEnviarEstampariaReinspecao").css("display","none")
    $("#btnEnviarEstamparia").css("display","block")

    $('#inspecionarEstamparia').modal('hide');

    $('#modalConfirmacaoEstamparia').modal('show');
})

$('#btnEnviarEstamparia').on('click',function() {

    $("#loading").show();

    var formData = new FormData();

    $('#btnEnviarEstamparia').prop('disabled',true);

    let id_inspecao = $('#inspecionarEstampariaLabel').text();
    let data_inspecao = $('#data_inspecao_estamparia').val();
    let inputCategoria = $('#inputMaquina_estamparia').val();
    let inputConjunto = $('#inputConjunto_estamparia').val();
    let inputPecasInspecionadasSolda = parseInt($('#inputPecasInspecionadas_estamparia').val());
    let inputConformidadesSolda = parseInt($('#inputConformidades_estamparia').val());
    let inputNaoConformidadesSolda = $('#inputNaoConformidades_estamparia').val();
    let inspetorSolda = $('#inspetor_estamparia').val();
    let list_causas = [];
    let list_quantidade = [];
    let outraCausaSolda = $('#outraCausa_estamparia').val();
    let observacaoSolda = $('#observacao_estamparia').val();
    let origemInspecaoSolda = $('#origemInspecao_estamparia').val();
    let tipos_causas_estamparia = $("#tipos_causas_estamparia").val()
    let reinspecao = 'False';

    if (inputConformidadesSolda === "" || inputConformidadesSolda > inputPecasInspecionadasSolda || inputConformidadesSolda < 0) {
        alert('Verifique se o campo de conformidades está com valor correto');
        $('#btnEnviarEstamparia').prop('disabled',false);
        $("#loading").hide();
        return; // Interrompe a execução
    }

    for (let i = 0; i < tipos_causas_estamparia; i++) {
        let causas = $("#causasEstamparia-" + i).val();
        let quantidade = $("#quantidade_causas_estamparia-" + i).val();
        let inputId = '#inputGroupFile_estamparia-' + i;
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
    formData.append('inspetorEstamparia', inspetorSolda);
    formData.append('num_pecas', inputPecasInspecionadasSolda);
    formData.append('inputConformidadesEstamparia', inputConformidadesSolda);
    formData.append('inputNaoConformidadesEstamparia', inputNaoConformidadesSolda);
    formData.append('list_causas', JSON.stringify(list_causas));
    formData.append('list_quantidade', JSON.stringify(list_quantidade));
    formData.append('outraCausaEstamparia', outraCausaSolda);
    formData.append('observacaoEstamparia', observacaoSolda);
    formData.append('origemInspecaoEstamparia', origemInspecaoSolda);
    formData.append('tipos_causas_estamparia',tipos_causas_estamparia);
    formData.append('reinspecao', reinspecao);

    $.ajax({
        url: '/inspecao-estamparia',
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