
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


$('#envio_reinspecao_solda').on('click',function() {

    var formData = new FormData();

    $('#envio_inspecao_solda').prop('disabled',true);

    let id_inspecao = $('#reinspecionarConjuntoLabel').text();
    let data_inspecao = $('#data_reinspecao_solda').val();
    let inputCategoria = $('#inputCategoria').val();
    let inputConjunto = $('#inputConjunto').val();
    let inputPecasInspecionadasSolda = $('#inputPecasInspecionadasSolda').val();
    let inputConformidadesSolda = $('#inputConformidadesSolda').val();
    let inputNaoConformidadesSolda = $('#inputNaoConformidadesSolda').val();
    let inspetoresSolda = []
    let causaSolda = $('#causaSolda').val();
    let outraCausaSolda = $('#outraCausaSolda').val();
    let observacaoSolda = $('#observacaoSolda').val();
    let origemInspecaoSolda = $('#origemInspecaoSoldaReinspecionadas').val();
    let reinspecao = 'False';

    if (inputConformidadesSolda.trim() === "" || inputConformidadesSolda.trim() > inputPecasInspecionadasSolda || inputConformidadesSolda.trim() < 0) {
        alert('Verifique se o campo de conformidades está com valor correto');
        $('#envio_inspecao_solda').prop('disabled',false);
        $("#loading").hide();
        return; // Interrompe a execução
    }

    if (causaSolda === null || observacaoSolda.trim() === "" ) {
        alert('Verifique se os campos de causa e observação estão com os valores corretos');
        $('#envio_inspecao_solda').prop('disabled',false);
        $("#loading").hide();
        return; // Interrompe a execução
    }
   
    $('select[id^="inspetorSolda"]').each(function() {
        if($(this).val() !== null){
            inspetoresSolda.push($(this).val()); // Adiciona o valor de cada select à lista
        } 
    });

    formData.append('id_inspecao', id_inspecao);
    formData.append('data_inspecao', data_inspecao);
    formData.append('inputCategoria', inputCategoria);
    formData.append('inputConjunto', inputConjunto);
    formData.append('inspetoresSolda', JSON.stringify(inspetoresSolda));
    formData.append('num_pecas', inputPecasInspecionadasSolda);
    formData.append('inputConformidadesSolda', inputConformidadesSolda);
    formData.append('inputNaoConformidadesSolda', inputNaoConformidadesSolda);
    formData.append('causaSolda', causaSolda);
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
            window.location.reload();
            console.log(response);
        },
        error: function (error) {
            console.log(error);
            $('#envio_inspecao_solda').prop('disabled',false);
        }
    });

})