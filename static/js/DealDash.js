
var inputAlert = false;
var checkAlert = false;

function search() {
    // Notify that the search button is clicked for debugging purposes
    console.log("Search button clicked!");

    // Grab the checkboxes
    var skipCB = document.getElementById("skipCheckbox");
    var ddCB = document.getElementById("ddCheckbox");
    var ueCB = document.getElementById("ueCheckbox");

    // Grab the input fields
    var addressField = document.getElementById("addressField");
    var userAddress = addressField.value;
    var foodField = document.getElementById("foodField");
    var userFood = foodField.value;

    // Notify what the current values are
    console.log(`Adress: ${userAddress}\nFood: ${userFood}\nUsing Skip: ${skipCB.checked}\nUsing DD: ${ddCB.checked}\nUsing UE: ${ueCB.checked}`);

    // Check for errors
    var error = false;

    // Check if there are blank values in any of the two input fields
    if (userAddress == "" || userFood == "") {
        // Debug to alert that this condition works
        console.log("Error, cannot start without a value for address or food!")

        if (inputAlert == false) {
            // Notify that we are creating the new text element
            console.log("Creating alert text...");

            // Create a new text that can be formatted to alert the user that they haven't texted anything in!
            var alertString = "Please put a value into food AND address!";
            var alertNode = document.createTextNode(alertString);
            var paraElem = document.createElement("p");
            paraElem.id = "inputAlertText";
            paraElem.appendChild(alertNode);

            // Set the color to red and bold
            paraElem.style = "color:red;font-weight:bold;";

            // Grab the inputFieldSection element and add this new text to it
            var inpFldSection = document.getElementById("inputFieldSection");
            inpFldSection.appendChild(paraElem);
            
            inputAlert = true;
        }
        error = true;
    } else {
        // Delete the alert alert texts if we previously created one.
        var inputAlertElem = document.getElementById("inputAlertText");
        if (inputAlertElem != null) {
            inputAlert = false;
            inputAlertElem.remove();
        }
    }

    // Make sure atleast one checkbox is clicked.
    if (skipCB.checked == false && ddCB.checked == false && ueCB.checked == false) {
        console.log("Error, cannot search without a delivery service...");

        if (checkAlert == false) {
            // Create a new text that can be formatted to alert the user that they haven't texted anything in!
            var alertString = "Please check atleast one delivery service before you search!";
            var alertNode = document.createTextNode(alertString);
            var paraElem = document.createElement("p");
            paraElem.id = "checkAlertText";
            paraElem.appendChild(alertNode);
            
            // Set the color to red and bold
            paraElem.style = "color:red;font-weight:bold;";
            
            // Grab the inputFieldSection element and add this new text to it
            var checkFldSection = document.getElementById("checkboxSection");
            checkFldSection.appendChild(paraElem);
                        
            checkAlert = true;
        }
        error = true;
    } else {
        // Delete the alert alert texts if we previously created one.
        var checkAlertElem = document.getElementById("checkAlertText");
        if (checkAlertElem != null) {
            checkAlert = false;
            checkAlertElem.remove();
        }
    }

    if (error) return;

    // Individually check which delivery services are checked, and call their corresponding scrapers.
    // var rests = [];
    if (skipCB.checked) {
        console.log("Launching Skip Scraper...");
        $.ajax({
            type: 'POST',
            url: "/skip",
            data: { address: userAddress, food: userFood }
        })
        .done(function(data) {
            // $('#output').text(data.address).show();
            $('#output').text(data.rests[0].name).show();
            createItems(data);
        });

    }
    if (ddCB.checked) {
        console.log("Launching DoorDash Scraper...");
        $.ajax({
            type: 'POST',
            url: "/dash",
            data: { address: userAddress, food: userFood }
        })
        .done(function(data) {
            // $('#output').text(data.address).show();

        });
    }
    if (ueCB.checked) {
        console.log("Launching UberEats Scraper...");
        $.ajax({
            type: 'POST',
            url: "/eats",
            data: { address: userAddress, food: userFood }
        })
        .done(function(data) {
            // $('#output').text(data.address).show();

        });
    }

}
function createItems(data){
    console.log(data);
    var i = 0;
    while (i<data.rests.length){
        var section = $("#output").append("<ul></ul>");
        const name = data.rests[i].name;
        const addr = data.rests[i].addr;
        const app = data.rests[i].app;
        const url = data.rests[i].url;
        const cpd = data.rests[i].rest_cpd;
        const dt = data.rests[i].deliv_time;
        const rc = data.rests[i].review_count;
        const df = data.rests[i].deliv_fee;
        const du = data.rests[i].dist_to_user;
        const rating = data.rests[i].rating;
        console.log(name);
        for (const m_key in data.rests[i].catalogue){
            const f_name = m_key.name;
            const f_desc = m_key.desc;
            const f_price = m_key.price;
            const f_image = m_key.image;
            const f_cal = m_key.calories;
            const f_cpd = m_key.cpd;
            console.log(f_name);
        }
        for (const d_key in data.rests[i].discounts){
            for (const discount in d_key){
                for (const discount_info in discount){

                }
            }
        }
        i++;
    }
    


    
}