$('#envio_inspecao').on('click',function () {
    
    let n_conformidades = $('#n_conformidades').val()
    let n_nao_conformidades = $('#n_nao_conformidades').val()
    let list_causas = []
    let foto_inspecao = selectedFiles;
    let inspetor = $("#inspetor").val()

    for(var i = 1;i <= n_nao_conformidades;i++){
        let causas = $("#causa_reinspecao_"+i).val()
        list_causas.push(causas)
    }  

    console.log(list_causas)
    console.log(foto_inspecao)
})