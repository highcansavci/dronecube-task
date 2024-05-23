document.addEventListener("DOMContentLoaded", function () {
            const create = document.getElementById("createButton");
            const update = document.getElementById("updateButton");

            const createButton = document.getElementById("submit-task")
            const updateButton = document.getElementById("update-task")
            const closeButton = document.getElementById("close-task")

            create.addEventListener("click", function () {
                document.getElementById("submit-task").style.display = "block";
                document.getElementById("update-task").style.display = "none";
            });

            update.addEventListener("click", function () {
                document.getElementById("submit-task").style.display = "none";
                document.getElementById("update-task").style.display = "block";
            });
});


function resetModal() {
    document.location.reload();
}