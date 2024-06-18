function modalTubos() {

    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);


    $('#data_tubos').val(today.toLocaleDateString());

    $('#inspetores_tubo').val('');
    $('#codigo_tubo').val('');
    $('#descricao_tubo').val('');
    $('#amassado_tubo').val('');
    $('#oxidacao_tubo').val('');
    $('#solda_tubo').val('');
   
    // Exibir o modal
    $('#tubosModal').modal('show');
}

function modalCilindros() {

    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);

    $('#data_cilindro').val(today.toLocaleDateString());

    $('#inspetores_cilindro').val('');
    $('#codigo_cilindro').val('');
    $('#descricao_cilindro').val('');
    $('#amassado_cilindro').val('');
    $('#oxidacao_cilindro').val('');
    $('#solda_cilindro').val('');
    $('#montador_cilindro').val('');

    // Exibir o modal
    $('#cilindrosModal').modal('show');
}

$("#codigo_cilindro").on('blur',function () {
    
    let lista_descricoes = ['CILINDRO HIDRÁULICO [CBH5/CBHM5000]','CILINDRO HIDRÁULICO [CBHM6000 CAFEEIRA]','CILINDRO HIDRÁULICO [CBH7/CBHM6000].']
    let codigo = $("#codigo_cilindro").val()

    if(codigo == '034550'){
        $('#descricao_cilindro').val(lista_descricoes[0]);
    } else if(codigo == '034630'){
        $('#descricao_cilindro').val(lista_descricoes[1]);
    } else if(codigo == '034830'){
        $('#descricao_cilindro').val(lista_descricoes[2]);
    } else {
        $('#descricao_cilindro').val('');
    }

})

$("#nao_conformidade_cilindro").on('input',function(){
    let nao_conformidade_cilindro =  $("#nao_conformidade_cilindro")

    if(nao_conformidade_cilindro.val() <= 0){
        $("#selectContainer").css('display','none')
    } else {
        $("#selectContainer").css('display','flex')
    }
})