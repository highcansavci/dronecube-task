var createOrUpdate = 0;
var currentTab = 0;

document.addEventListener("DOMContentLoaded", function () {
            const create = document.getElementById("createButton");
            const update = document.getElementById("updateButton");

            const createButton = document.getElementById("submit-drone")
            const updateButton = document.getElementById("update-drone")
            const closeButton = document.getElementById("close-drone")

            create.addEventListener("click", function () {
                document.getElementById("submit-drone").style.display = "none";
                document.getElementById("update-drone").style.display = "none";
                createOrUpdate = 1;
            });

            update.addEventListener("click", function () {
                document.getElementById("submit-drone").style.display = "none";
                document.getElementById("update-drone").style.display = "none";
                createOrUpdate = 2;
            });

            createButton.addEventListener("click", function () {
                currentTab = 0;
            });

            updateButton.addEventListener("click", function () {
                currentTab = 0;
            });
});


document.addEventListener("DOMContentLoaded", function(event) {
    showTab(currentTab);
});

function resetModal() {
    document.location.reload();
}

function showTab(n) {
    var x = document.getElementsByClassName("tab");
    if (n < x.length) {
        x[n].style.display = "block";
    }
    if (n == 0) {
        document.getElementById("prevBtn").style.display = "none";
    } else {
        document.getElementById("prevBtn").style.display = "inline";
    }
    if (n == (x.length - 1)) {
        document.getElementById("nextBtn").innerHTML = '<i class="fa fa-angle-double-right"></i>';
    } else {
        document.getElementById("nextBtn").innerHTML = '<i class="fa fa-angle-double-right"></i>';
    }
    fixStepIndicator(n)
}

function nextPrev(n) {
    var x = document.getElementsByClassName("tab");
    if (n == 1 && !validateForm()) return false;
    x[currentTab].style.display = "none";
    currentTab = currentTab + n;
    if (currentTab >= x.length) {
        document.getElementById("nextprevious").style.display = "none";
        document.getElementById("all-steps").style.display = "none";
        document.getElementById("register").style.display = "none";
        document.getElementById("text-message").style.display = "block";
        if (createOrUpdate == 1) {
            document.getElementById("submit-drone").style.display = "block";
        }
        else if (createOrUpdate == 2) {
            document.getElementById("update-drone").style.display = "block";
        }
    } else {

    }
    showTab(currentTab);
}

function int(value) {
    return parseInt(value);
}

function checkValue(sender) {
    if (sender.type == "number") {
        let min = int(sender.min);
        let max = int(sender.max);
        let value = int(sender.value);
        return (isNaN(min) && isNaN(max)) || (!isNaN(min) && !isNaN(max) && min <= value && value <= max);
    }
    return true;
}

function validateForm() {
    var x, y, i, valid = true;
    x = document.getElementsByClassName("tab");
    y = x[currentTab].getElementsByTagName("input");
    for (i = 0; i < y.length; i++) {
        if (y[i].value == "" || !checkValue(y[i])) {
            y[i].className += " invalid";
            valid = false;
        }
    }
    if (valid) {
        document.getElementsByClassName("step")[currentTab].className += " finish";
    }
    return valid;
}

function fixStepIndicator(n) {
    var i, x = document.getElementsByClassName("step");
    for (i = 0; i < x.length; i++) {
        x[i].className = x[i].className.replace(" active", "");
    }
    if (n < x.length) {
        x[n].className += " active";
    }
}

