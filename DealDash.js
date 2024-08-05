
var alert = false;

function search() {
    // Notify that the search button is clicked for debugging purposes
    console.log("Search button clicked!");

    // Grab the checkboxes
    var skipCB = document.getElementById("skipCheckbox");
    var ddCB = document.getElementById("ddCheckbox");
    var ueCB = document.getElementById("ueCheckbox");

    // Grab the input fields
    var addressField = document.getElementById("addressField");
    var address = addressField.value;
    var foodField = document.getElementById("foodField");
    var food = foodField.value;

    // Notify what values are currently in the field
    console.log(`Adress: ${address}\nFood: ${food}\nUsing Skip: ${skipCB.checked}\nUsing DD: ${ddCB.checked}\nUsing UE: ${ueCB.checked}`);

    // Check if there are blank values in any of the two input fields
    if (address == "" || food == "") {
        // Debug to alert that this condition works
        console.log("Error, cannot start without a value for address or food!")

        if (alert == false) {
            // Notify that we are creating the new text element
            console.log("Creating alert text...");

            // Create a new text that can be formatted to alert the user that they haven't texted anything in!
            var alertString = "Please put a value into food AND address!";
            var alertNode = document.createTextNode(alertString);
            var paraElem = document.createElement("p");
            paraElem.id = "alertText";
            paraElem.appendChild(alertNode);

            // Set the color to red and bold
            paraElem.style = "color:red;font-weight:bold;";

            // Grab the inputFieldSection element and add this new text to it
            var inpFldSection = document.getElementById("inputFieldSection");
            inpFldSection.appendChild(paraElem);
            
            alert = true
        }
        return
    }

    // Delete the text if we previously created one.
    var alertParaElem = document.getElementById("alertText");
    if (alertParaElem != null) {
        alert = false;
        alertParaElem.remove();
    }
}