let data = "";
let display = document.getElementById("get");

function updateDisplay(value) {
    data += value; 
    display.innerText = data;
}


function clearDisplay() {
    data = ""; 
    display.innerText = ""; 
}

function calculateResult() {
    try {
        let result = eval(data.replace("^", "**"));
        display.innerText = result; 
        data = result.toString(); 
    } catch (error) {
        display.innerText = "Error"; 
        data = ""; 
    }
}

document.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", (e) => {
        let id = e.target.id; 
        if (id === "clear") {
            clearDisplay();
        } else if (id === "equal") {
            calculateResult();
        } else {
            let value = id === "Mul" ? "*" : id === "divison" ? "/" : id === "reminder" ? "%" : id === "pow" ? "^" : e.target.innerText;
            updateDisplay(value);
        }
    });
});
