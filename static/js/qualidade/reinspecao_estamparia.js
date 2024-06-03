
function modalReinspecaoEstamparia(id,data, n_nao_conformidades,conjunto,categoria) {

    // Configurar o conteúdo do modal com os parâmetros recebidos
    $('#reinspecionarConjuntoLabel').text(id)
    $('#data_reinspecao_estamparia').val(formatarDataBrSemHoraEs(data));
    $('#inputPecasReinspecionadas_estamparia').val(n_nao_conformidades)
    $("#inputConjuntoReinspecao_estamparia").val(conjunto);
    $("#maquina_reinspecao_estamparia").val(categoria);
    
    // Exibir o modal
    $('#reinspecaoModalEstamparia').modal('show');

}

function formatarDataBrSemHoraEs(dataString) {
    // Cria um objeto Date a partir da string
    var data = new Date(dataString);

    data.setDate(data.getDate());

    // Obtém os componentes da data
    var dia = data.getDate().toString().padStart(2, '0');
    var mes = (data.getMonth() + 1).toString().padStart(2, '0');
    var ano = data.getFullYear();

    var formatoDesejado = `${dia}/${mes}/${ano}`;

    return formatoDesejado;
}

$('#inputReinspecionadasConformidades_estamparia').on('input',function() {

    let pecasInspecionadasSolda = $('#inputPecasReinspecionadas_estamparia').val();
    let numConformidadesSolda = $('#inputReinspecionadasConformidades_estamparia').val();
    let numNaoConformidadesSolda = $('#inputReinspecionadasNaoConformidades_estamparia');
    let outraCausaSoldaReinspecionadas = $("#outraCausaReinspecionadas_estamparia");

    numNaoConformidadesSolda.val(pecasInspecionadasSolda - numConformidadesSolda);

    if(numConformidadesSolda === ''){
        numNaoConformidadesSolda.val('')
    }

    if(numNaoConformidadesSolda.val() === '' || numNaoConformidadesSolda.val() <= 0 || numConformidadesSolda < 0){
        outraCausaSoldaReinspecionadas.prop('disabled',true);
        outraCausaSoldaReinspecionadas.val('')
    } else {
        outraCausaSoldaReinspecionadas.prop('disabled',false);
        outraCausaSoldaReinspecionadas.val('')
    }

})

$('#envio_reinspecao_estamparia').on('click',function() {
    let inputConformidadesSolda = parseInt($('#inputReinspecionadasConformidades_estamparia').val());
    let inputNaoConformidadesSolda = parseInt($('#inputReinspecionadasNaoConformidades_estamparia').val());
    let inputPecasInspecionadasSolda = parseInt($('#inputPecasReinspecionadas_estamparia').val());
    let inputConjunto = $('#inputConjuntoReinspecao_estamparia').val();
    let observacaoSolda = $('#observacaoReinspecionadas_estamparia').val();
    let inspetoresSolda = $('#inspetoresReinspecao_estamparia').val();
    let retrabalhoSolda = $('#retrabalho_estamparia').val();

    $("#confirmarConformidades_estamparia").val(inputConformidadesSolda);
    $("#confirmarNaoConformidades_estamparia").val(inputNaoConformidadesSolda);

    $('#modalConfirmacaoEstamparia #p_confirmar_inspecao_estamparia').text("Deseja confirmar as informações preenchidas referente a reinspeção do conjunto " + inputConjunto);

    $("#btnEnviarEstampariaReinspecao").css("display","block")
    $("#btnEnviarEstamparia").css("display","none")

    if (inputConformidadesSolda === "" || inspetoresSolda === null || retrabalhoSolda === null || inputConformidadesSolda > inputPecasInspecionadasSolda || inputConformidadesSolda < 0) {
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
            alert('Preencha todos os campos das causas de não conformidade.');
            $('#btnEnviarEstampariaReinspecao').prop('disabled',false);
            $("#loading").hide();
            return; // Interrompe a execução
        }
    }

    $('#reinspecaoModalEstamparia').modal('hide');

    $('#modalConfirmacaoEstamparia').modal('show');
})

$('#btnEnviarEstampariaReinspecao').on('click',function() {

    $("#loading").show();

    var formData = new FormData();

    $('#btnEnviarEstampariaReinspecao').prop('disabled',true);

    let id_inspecao = $('#reinspecionarConjuntoLabel').text();
    let data_inspecao = $('#data_reinspecao_estamparia').val();
    let inputCategoria = $('#maquina_reinspecao_estamparia').val();
    let inputConjunto = $('#inputConjuntoReinspecao_estamparia').val();
    let inputPecasInspecionadasSolda = parseInt($('#inputPecasReinspecionadas_estamparia').val());
    let inputConformidadesSolda = parseInt($('#inputReinspecionadasConformidades_estamparia').val());
    let inputNaoConformidadesSolda = parseInt($('#inputReinspecionadasNaoConformidades_estamparia').val());
    let inspetorSolda = $('#inspetoresReinspecao_estamparia').val();
    let retrabalhoSolda = $('#retrabalho_estamparia').val();
    let list_causas = [];
    let list_quantidade = [];
    let outraCausaSolda = $('#outraCausaReinspecionadas_estamparia').val();
    let observacaoSolda = $('#observacaoReinspecionadas_estamparia').val();
    let origemInspecaoSolda = $('#origemReinspecionadas_estamparia').val();
    let tipos_causas_estamparia = $("#tipos_causas_estamparia_reinspecao").val()
    let reinspecao = "True";

    for (var i = 0; i < tipos_causas_estamparia; i++) {
        let causas = $("#causasEstampariaR-" + i).val();
        let quantidade = $("#quantidade_causas_estampariaR-" + i).val();
        let inputId = '#inputGroupFile_estampariaR-' + i;
        let files = $(inputId)[0].files;

        if (causas === "" || quantidade === "") {
            alert('Preencha todos os campos das causas de não conformidade.');
            $("#loading").hide();
            return; // Interrompe a execução
        }
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
    formData.append('retrabalhoSolda', retrabalhoSolda);
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
            $('#btnEnviarSoldaReinspecao').prop('disabled',false);
        }
    });

})