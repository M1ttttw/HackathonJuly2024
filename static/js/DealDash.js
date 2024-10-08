
function search() {
    var has_btn = false;

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
    var loadCnt = Number($("#loadCount").val());
    $("#inputErr").hide();
    $("#intErr").hide();
    $("#restErr").hide();
    // Notify what the current values are
    console.log(`Adress: ${userAddress}\nFood: ${userFood}\nUsing Skip: ${skipCB.checked}\nUsing DD: ${ddCB.checked}\nUsing UE: ${ueCB.checked}`);

    // Check for errors
    // Check if there are blank values in any of the two input fields
    if (userAddress == "" || userFood == "") {
        // Debug to alert that this condition works
        console.log("Error, cannot start without a value for address or food!")
        $("#inputErr").show();
        return;
    
    } else if (isNaN(loadCnt)){
        $("#intErr").show();
        return;
    }

    // Make sure atleast one checkbox is clicked.
    if (skipCB.checked == false && ddCB.checked == false && ueCB.checked == false) {
        console.log("Error, cannot search without a delivery service...");
        $("#restErr").show();
        return;
    }

    // Remove/Add UI elements when performing the search
    $("#srchBtn").hide();
    $("#loadingAnim").show();
    // Use a ajax request, and pass in our check box values + address and food.
    $.ajax({
        type: 'POST',
        url: "/scrape",
        data: { address: userAddress, food: userFood, skip: skipCB.checked, dash: ddCB.checked, eats: ueCB.checked ,loadCnt},
        success: function(data) {
            // Create UI elements and display them based off the data we get back
            $( "#output" ).remove();
            $("body").append("<div id='output'></div>");
            createItems(data);
            if (!has_btn){
                $("#loadingAnim").hide();
                $("#srchBtn").show();
            }
        },
        error: function(error) {
            console.log(`Request to server failed!`);
            if (!has_btn){
                $("#loadingAnim").hide();
                $("#srchBtn").show();
            }
        }
    });

}
function createItems(data){
    has_btn = true;
    console.log(data);
    var rest_cnt = 0;
    // for all entries in our restaurants json we create an element for each one
    for (let rest_name in data.rests) {

        let rest = data.rests[rest_name];
        let name = rest["name"];
        let addr = rest["addr"];
        let app = rest["app"];
        let url = rest["url"];
        let image = rest["image"];
        let cpd = rest["rest_cpd"];
        let dt = rest["deliv_time"];
        let rc = rest["review_count"];
        let df = rest["deliv_fee"];
        let du = rest["dist_to_user"];
        let rating = rest["rating"];
        let cat = rest["catalogue"];
        let discounts = rest["discounts"];
        //add restaurant container
        var descs = $("#output").append("<div class='restaurant' id="+rest_cnt.toString()+"></div>");
        console.log(name);
        if (image != "") $("<img src='"+image+"'>").appendTo(`#${rest_cnt}`);
        //add attributes of restaurant
        $("<p> name:"+ name +"</p>").appendTo(`#${rest_cnt}`);
        $("<p> address:"+ addr+"</p>").appendTo(`#${rest_cnt}`);
        $(`<p> app: ${app}</p>`).appendTo(`#${rest_cnt}`);
        $("<p> url: "+url+"</p>").appendTo(`#${rest_cnt}`);
        if (dt>0) $(`<p> delivery time: ${dt}</p>`).appendTo(`#${rest_cnt}`);
        if (rc>0)$(`<p> review count: ${rc}</p>`).appendTo(`#${rest_cnt}`);
        if (df>0)$(`<p>delivery fee: ${df}</p>`).appendTo(`#${rest_cnt}`);
        if (du>0)$(`<p>distance: ${du}</p>`).appendTo(`#${rest_cnt}`);
        if (rating>0)$(`<p>rating: ${rating}</p>`).appendTo(`#${rest_cnt}`);
        // create the dropdown menu for the food items
        $(`#${rest_cnt}`).append(`<div id='${rest_cnt}_menu' class='menu'></div>`);
        var food_cnt = 0;
        var max_food_cnt = 5;
        //add the food items
        for (let food_name in cat) {
            let food_item = cat[food_name];
            let f_name = food_item["name"];
            let f_desc = food_item["desc"];
            let f_price = food_item["price"];
            let f_image = food_item["image"];
            let f_cal = food_item["calories"];
            let f_cpd = food_item["cpd"];
            $(`<div id='${rest_cnt}_${food_cnt}' class='item'></div>`).appendTo(`#${rest_cnt}_menu`);
            if (f_image != "") { $("<img src='"+f_image+"'>").appendTo(`#${rest_cnt}_${food_cnt}`); }
            $("<p>item name:"+f_name+"</p>").appendTo(`#${rest_cnt}_${food_cnt}`);
            $("<p>item description:"+f_desc+"</p>").appendTo(`#${rest_cnt}_${food_cnt}`);
            $(`<p>item price:${f_price}\$</p>`).appendTo(`#${rest_cnt}_${food_cnt}`);
            console.log(f_name);
            food_cnt ++;
            if (food_cnt == max_food_cnt){
                break;
            }
        }
        //create the discount container
        $(`#${rest_cnt}`).append(`<ul id='${rest_cnt}_discount'></ul>`);
        //add discounts to the container
        for (let d_type in discounts) {
            var discount_cnt = 0;
            disc_args = discounts[d_type];
            for (discount_arg of disc_args) {
                var discount_str = "";
                console.log(disc_args);
                //parses json response to generate discount string
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
                    $(`<il id='${rest_cnt}_${discount_cnt}'><p>`+discount_str+"</p></il>").appendTo(`#${rest_cnt}_discount`); 
                    discount_cnt ++;
                }
            }
            
        }
        rest_cnt ++;
    }


    
}