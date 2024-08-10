
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
            url: "/scrape",
            data: { address: userAddress, food: userFood, scrape_type: 0 }
        })
        .done(function(data) {
            // $('#output').text(data.address).show();
//            $('#output').text(data.rests[0].name).show();
            createItems(data);
        });

    }
    if (ddCB.checked) {
        console.log("Launching DoorDash Scraper...");
        $.ajax({
            type: 'POST',
            url: "/scrape",
            data: { address: userAddress, food: userFood, scrape_type: 1 }
        })
        .done(function(data) {
            // $('#output').text(data.address).show();

        });
    }
    if (ueCB.checked) {
        console.log("Launching UberEats Scraper...");
        $.ajax({
            type: 'POST',
            url: "/scrape",
            data: { address: userAddress, food: userFood, scrape_type: 2 }
        })
        .done(function(data) {
            // $('#output').text(data.address).show();

        });
    }

}
function createItems(data){
    console.log(data);
    var rest_cnt = 0;
    for (let rest_name in data.rests) {

        let rest = data.rests[rest_name];
        let name = rest["name"];
        let addr = rest["addr"];
        let app = rest["app"];
        let url = rest["url"];
        let cpd = rest["rest_cpd"];
        let dt = rest["deliv_time"];
        let rc = rest["review_count"];
        let df = rest["deliv_fee"];
        let du = rest["dist_to_user"];
        let rating = rest["rating"];
        let cat = rest["catalogue"];
        let discounts = rest["discounts"];
        var descs = $("#output").append("<div id="+rest_cnt.toString()+"></div>");
        console.log(name);
        $("<p> name:"+ name +"</p>").appendTo(`#${rest_cnt}`);
        $("<p> address:"+ addr+"</p>").appendTo(`#${rest_cnt}`);
        $(`<p> app: ${app}</p>`).appendTo(`#${rest_cnt}`);
        $("<p> url: "+url+"</p>").appendTo(`#${rest_cnt}`);
        $(`<p> delivery time: ${dt}</p>`).appendTo(`#${rest_cnt}`);
        $(`<p> review count: ${rc}</p>`).appendTo(`#${rest_cnt}`);
        $(`<p>delivery fee: ${df}</p>`).appendTo(`#${rest_cnt}`);
        $(`<p>distance: ${du}</p>`).appendTo(`#${rest_cnt}`);
        $(`<p>rating: ${rating}</p>`).appendTo(`#${rest_cnt}`);
        $(`#${rest_cnt}`).append(`<ul id='${rest_cnt}_menu'></ul>`);
        var food_cnt = 0;
        var max_food_cnt = 5;
        for (let food_name in cat) {
            let food_item = cat[food_name];
            let f_name = food_item["name"];
            let f_desc = food_item["desc"];
            let f_price = food_item["price"];
            let f_image = food_item["image"];
            let f_cal = food_item["calories"];
            let f_cpd = food_item["cpd"];
            $(`<il id='${rest_cnt}_${food_cnt}'></il>`).appendTo(`#${rest_cnt}_menu`);
            $("<img src='"+f_image+"'>").appendTo(`#${rest_cnt}_${food_cnt}`);
            $("<p>item name:"+f_name+"</p>").appendTo(`#${rest_cnt}_${food_cnt}`);
            $("<p>item description:"+f_desc+"</p>").appendTo(`#${rest_cnt}_${food_cnt}`);
            $(`<p>item price:${f_price}\$</p>`).appendTo(`#${rest_cnt}_${food_cnt}`);
            console.log(f_name);
            food_cnt ++;
            if (food_cnt == max_food_cnt){
                break;
            }
        }
        $(`#${rest_cnt}`).append(`<ul id='${rest_cnt}_discount'></ul>`);
        for (let d_type in discounts) {
            var discount_cnt = 0;
            disc_args = discounts[d_type];
            for (discount_arg of disc_args) {
                var discount_str = "";
                console.log(disc_args);
                if (app === "SkipTheDishes"){
                    if (d_type == 1){
                        discount_str =  "Free "+ discount_arg[0] + ` on purchases ${discount_arg[1]}$ +`;

                    }else if (d_type == 2){
                        discount_str = `${discount_arg[0]}$ off with `+ `${discount_arg[1]}$ purchase+`;
                    }
                }else if(app === "UE"){
                    if (d_type == 1){
                        discount_str =  "Buy One Get One Free For "+ discount_arg[0];
                    }else if(d_type==2){
                        discount_str ="Free "+ discount_arg[0]+ ` on purchases ${discount_arg[1]}$ +`;
                    }else if(d_type==3){
                        discount_str = `0$ delivery on orders ${discount_arg[0]}$+`;

                    }else if(d_type==4){
                        discount_str =  `Save ${discount_arg[0]}$`+ ` (up to ${discount_arg[1]}$)`+ ` when you order ${discount_arg[2]}$ or more`;
                    }
                }else if(app==="DD"){
                    if(d_type==1){
                        discount_str = "Free "+ discount_arg[0] + ` on purchases ${discount_arg[1]}$ +`;
                    }else if(d_type==2){
                        discount_str = `${discount_arg[0]}% off`+ ` on orders ${discount_arg[1]}$ +`;
                    }else if(d_type==3){
                        discount_str = `0$ delivery on orders ${discount_arg[0]}$+`;
                    }
                }
                
                if (discount_str.length>0){
                    $(`<il id='${rest_cnt}_${discount_cnt}'>`+discount_str+"</il>").appendTo(`#${rest_cnt}_discount`); 
                    discount_cnt ++;
                }
            }
            
        }
        rest_cnt ++;
    }


    
}