
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
            $('#output').text(data.rest_1).show();
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
    const rests = JSON.parse(data);
    for (const key in rests) {
        var section = $("#output").append("<ul></ul>");
        const rest_data = JSON.parse(rests[key]);
        const name = rest_data.name;
        const addr = rest_data.addr;
        const app = rest_data.app;
        const url = rest_data.url;
        const cpd = rest_data.rest_cpd;
        const dt = rest_data.deliv_time;
        const rc = rest_data.review_count;
        const df = rest_data.deliv_fee;
        const du = rest_data.dist_to_user;
        const rating = rest_data.rating;
        const menu = JSON.parse(rest_data.catalogue);
        for (const m_key in menu){
            const food_data = JSON.parse(menu[m_key]);
            const f_name = food_data.name;
            const f_desc = food_data.desc;
            const f_price = food_data.price;
            const f_image = food_data.image;
            const f_cal = food_data.calories;
            const f_cpd = food_data.cpd;
        }
        const discounts = JSON.parse(rest_data.discounts);
        for (const d_key in discounts){
            const disnt_data = JSON.parse(discounts[d_key]);
            for (const discount in disnt_data){
                for (const discount_info in discount){

                }
            }
        }
    }
    


    
}