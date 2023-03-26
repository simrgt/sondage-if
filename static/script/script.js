$(document).ready(function () {
    var otherCheckbox = $('#RMatin');
    otherCheckbox.click(function () {
        if (otherCheckbox[0].checked == true) {
            $(".cache")[0].style.display = "block";

        } else {
            $(".cache")[0].style.display = "none";
        }
    });
    var otherCheckbox2 = $('#RSoir');
    otherCheckbox2.click(function () {
        if (otherCheckbox2[0].checked == true) {
            $(".cache2")[0].style.display = "block";

        } else {
            $(".cache2")[0].style.display = "none";
        }
    });
    init();
});

let ssGrp= {};
let ssSsGrp = {};
let aliments = {};

function init() {
    let div_select = $(".cache2 > div, .cache > div");
    let groupe_select = div_select.find("select[id='groupe']");
    //console.log(groupe_select);
    let sousGroupe_select = div_select.find("select[id='sous_groupe']");
    let sousSousGroupe_select = div_select.find("select[id='sous_sous_groupe']");
    //let aliment_select = $("#aliment");
    groupe_select.each( function () {
        this.onchange = function () {
            changeSsGrp(this);
            // cacherListe(this);
        };
    });
    sousGroupe_select.each( function () {
        this.onchange = function () {
            changeSsSsGrp(this);
        };
    });
    sousSousGroupe_select.each( function () {
        this.onchange = function () {
            changeAliment2(this);
        };
    });
    groupe_select.each(function () {
        changeSsGrp(this);
    });
}

async function changeSsGrp(parent) {
    cacherListe(parent);
    let sousGroupe = parent.parentElement.children.sous_groupe;
    let groupe_val = parent.value;
    if (!(groupe_val === "Non Selectionné")) {
        if (groupe_val in ssGrp) {
            let optionHTML = '';
            for (let sousGroupe of ssGrp[groupe_val]) {
                optionHTML += '<option value="' + sousGroupe.id + '">' + sousGroupe.name + '</option>';
            }
            sousGroupe.innerHTML = optionHTML;
            changeSsSsGrp(sousGroupe);
        } else {
            await fetch('/api/sousGroupe/' + groupe_val).then(function (response) {
                response.json().then(function (data) {
                    ssGrp[groupe_val] = data.sousGroupe;
                    let optionHTML = '';
                    for (let sousGroupe of data.sousGroupe) {
                        optionHTML += '<option value="' + sousGroupe.id + '">' + sousGroupe.name + '</option>';
                    }
                    sousGroupe.innerHTML = optionHTML;
                    changeSsSsGrp(sousGroupe);
                });
            });
        }
    }
}
function changeSsSsGrp(parent) {
    let sousSousGroupe = parent.parentElement.children.sous_sous_groupe;
    let groupe_val = parent.value;
    if (groupe_val in ssSsGrp) {
        let optionHTML = '';
        for (let sousSousGroupe of ssSsGrp[groupe_val]) {
            optionHTML += '<option value="' + sousSousGroupe.id + '">' + sousSousGroupe.name + '</option>';
        }
        sousSousGroupe.innerHTML = optionHTML;
        console.log(sousSousGroupe);
        console.log(sousSousGroupe.options.length);
        if (sousSousGroupe.options.length <= 1) {
            console.log("cacher");
            cacher(sousSousGroupe);
        } else {
            afficher(sousSousGroupe);
        }
        changeAliment2(sousSousGroupe);
    } else {
        fetch('/api/sousSousGroupe/' + groupe_val).then(function (response) {
            response.json().then(function (data) {
                ssSsGrp[groupe_val] = data.sousSousGroupe;
                if (data.sousSousGroupe.length <= 1) {
                    cacher(sousSousGroupe);
                } else {
                    afficher(sousSousGroupe);
                }
                let optionHTML = '';
                for (let sousSousGroupe of data.sousSousGroupe) {
                    optionHTML += '<option value="' + sousSousGroupe.id + '">' + sousSousGroupe.name + '</option>';
                }
                sousSousGroupe.innerHTML = optionHTML;
                changeAliment2(sousSousGroupe);
            });
        });
    }
}

function changeAliment2(parent) {
    let aliment = parent.parentElement.children.aliment;
    let groupe_val = parent.value;
    if (groupe_val in aliments) {
        let optionHTML = '';
        for (let aliment of aliments[groupe_val]) {
            optionHTML += '<option value="' + aliment.id + '">' + aliment.name + '</option>';
        }
        aliment.innerHTML = optionHTML;
        return;
    } else {
        fetch('/api/aliment/' + groupe_val).then(async function (response) {
            response.json().then(function (data) {
                aliments[groupe_val] = data.aliment;
                let optionHTML = '';
                for (let aliment of data.aliment) {
                    optionHTML += '<option value="' + aliment.id + '">' + aliment.name + '</option>';
                }
                aliment.innerHTML = optionHTML;
            });
        });
    }

}

function cacher(element) {
    element.style.display = "none";
}

function afficher(element) {
    element.style.display = "block";
}
let groupes;
let prt;
function cacherListe(parent) {
    prt = parent;
    let div = parent.parentElement.parentElement;
    groupes = div.children;
    let index = false;
    for (let i = 0; i < groupes.length; i++) {
        for (let j = 0; j < groupes.item(i).children.length; j++) {
            if (!index)
                    afficher(groupes.item(i).children.item(j));
            else
                cacher(groupes.item(i).children.item(j));
            if (groupes.item(i).children.groupe.value === "Non Selectionné")
                index = true;
        }
    }
}