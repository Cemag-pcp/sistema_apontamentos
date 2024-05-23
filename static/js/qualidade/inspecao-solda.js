function modalInspecionarConjunto(id_inspecao,categoria,conjunto,quantidade) {

    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);

    $('#inspecionarConjuntoLabel').text(id_inspecao)

    $('#inspecionarConjunto input').val('');
    $('#inspecionarConjunto select').val(null);
    $('#inspecionarConjunto textarea').val('');

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
    let causaSolda = $("#causaSolda");
    let origemInspecaoSoldaReinspecionadas = $('#origemInspecaoCol');

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
        origemInspecaoSoldaReinspecionadas.css('display','none')
        origemInspecaoSoldaReinspecionadas.val(null)
        $('#outraCausaSolda').val('')
    } else {
        selectNaoConformidadesSolda.prop('disabled',false);
        causaSolda.prop('disabled',false);
        origemInspecaoSoldaReinspecionadas.css('display','block')
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

    var formData = new FormData();

    $('#envio_inspecao_solda').prop('disabled',true);

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
        $('#envio_inspecao_solda').prop('disabled',false);
        $("#loading").hide();
        return; // Interrompe a execução
    }

    for (var i = 1; i <= inputNaoConformidadesSolda; i++) {
        let causas = $("#causa_reinspecao_" + i).val();
        if (causas.trim() === "") {
            alert('Por favor, preencha todos os campos de causas de não conformidade.');
            $('#envio_inspecao').prop('disabled',false);
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
            window.location.reload();
            console.log(response);
        },
        error: function (error) {
            console.log(error);
            $('#envio_inspecao_solda').prop('disabled',false);
        }
    });

})