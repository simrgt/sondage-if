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
});
