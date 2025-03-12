console.log("Talk2Me script loaded");

document.addEventListener("DOMContentLoaded", function() {
    const buttons = document.querySelectorAll("button");
    buttons.forEach(button => {
        button.addEventListener("click", () => {
            console.log("Button clicked!");
        });
    });
});
