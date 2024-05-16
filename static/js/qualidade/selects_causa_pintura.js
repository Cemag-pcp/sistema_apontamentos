// Array com as causas
var causas = ["Faltando Solda", "Olho de Peixe", "Arranhão", "Escorrimento", "Empoeiramento","Casca de Laranja","Manchas",
"Contato","Amassando","Camada Baixa","Corrosão","Marcação por Água","Marcação por Óleo","Tonalidade","Marca texto industrial","Respingo de Solda",
"Marcação de Peça","Falta de aderência","Decapante","Desplacamento","Água"];

function adicionarSelects(n_nao_conformidades,coluna_causa,coluna_arquivos) {
    var n_nao_conformidades = document.getElementById(n_nao_conformidades).value;
    var coluna_causa = document.getElementById(coluna_causa);
    var coluna_arquivos = document.getElementById(coluna_arquivos);

    coluna_causa.innerHTML = "";

    var div_row = document.createElement('div');
    div_row.className = 'row';

    if (n_nao_conformidades > 0) {
        coluna_causa.style.display = 'block';
        coluna_arquivos.style.display = 'block';
        for (var i = 1; i <= n_nao_conformidades; i++) {
            var div = document.createElement("div");
            div.className = "col-sm-6 mb-4";

            var label = document.createElement("label");
            label.textContent = "Causa " + i;

            var select = document.createElement("select");
            select.name = "causa_reinspecao_" + i;
            select.id = "causa_reinspecao_" + i;
            select.className = "form-control";

            // Adiciona a opção vazia
            var optionHidden = document.createElement("option");
            optionHidden.value = "";
            optionHidden.selected = true;
            optionHidden.hidden = true;
            select.appendChild(optionHidden);

            // Adiciona as opções das causas do array
            for (var j = 0; j < causas.length; j++) {
                var option = document.createElement("option");
                option.value = causas[j];
                option.textContent = causas[j];
                select.appendChild(option);
            }

            div.appendChild(label);
            div.appendChild(select);
            div_row.appendChild(div)
            coluna_causa.appendChild(div_row);
        }
    } else {
        coluna_causa.style.display = 'none';
        coluna_arquivos.style.display = 'none';
    }
}

document.getElementById("foto_inspecao").addEventListener("change", function() {
    var files = this.files;
    var label = document.querySelector('.custom-file-label');
    var fileNames = [];
    for (var i = 0; i < files.length; i++) {
        fileNames.push(files[i].name);
    }
    if(files.length == 1){
        label.textContent = "Possui " + files.length + " arquivo";
    } else if(files.length == 0){
        label.textContent = "";
    } else {
        label.textContent = "Possui " + files.length + " arquivos";
    }
});

document.getElementById("foto_reinspecao").addEventListener("change", function() {
    var files = this.files;
    console.log(files)
    var label = document.querySelector('.label-reinspecao');
    var fileNames = [];
    for (var i = 0; i < files.length; i++) {
        fileNames.push(files[i].name);
    }
    if(files.length == 1){
        label.textContent = "Possui " + files.length + " arquivo";
    } else if(files.length == 0){
        label.textContent = "";
    } else {
        label.textContent = "Possui " + files.length + " arquivos";
    }
});

// Event listener para chamar a função quando o valor de n_nao_conformidades mudar
document.getElementById("n_conformidades").addEventListener("input", function() {
    adicionarSelects("n_nao_conformidades","coluna_causa","campo_arquivos");
});

document.getElementById("n_conformidades_reinspecao").addEventListener("input", () => {
    adicionarSelects("n_nao_conformidades_reinspecao","coluna_causa_reinspecao","campo_arquivos_reinspecao");
});
