import * as signalR from "@microsoft/signalr";

const negotiateUrl = "http://localhost:7071/api";
// const negotiateUrl = "https://smarthighwayfunctionapp.azurewebsites.net/api";

const connection = new signalR.HubConnectionBuilder()
    .withUrl(`${negotiateUrl}`)
    // .withAutomaticReconnect()
    .configureLogging(signalR.LogLevel.Information)
    .build();


async function start() {
    try {
        await connection.start();
        console.log("SignalR Connected.");
    } catch (err) {
        console.log(err);
        setTimeout(start, 5000);
    }
};


connection.onclose(async () => {
        await start();
});

connection.on("newMessage", (values, numCarsDict) => {
    var lights = {"t1": ["north", "south"], "t2": ["south, east"]};
    var state_to_color = {0: "Red", 1:"Green"};
    var laneNames = {"east_t2": "East to West", "west_t2": "West to East",
                    "north_t1": "North to South", "south_t1": "South to North"}

    for (const [lightId, directions] of Object.entries(lights)){
        for (var i = 0; i < xs.length; i++){
            var direction = directions[i];
            var lightElem = document.getElementById(`light_${direction}_${lightId}`);
            var oppositeDirection = directions[1 - i];
            var content = document.createTextNode(`${direction} to ${oppositeDirection} is ${state_to_color[values[lightId]]}`);
            lightElem.innerHTML = ``;
            var fontElem = document.createElement("font");
            fontElem.appendChild(content);
            fontElem.setAttribute("color", state_to_color[values[lightId]].toLowerCase());
            lightElem.appendChild(fontElem);
        }
    }
    // var t1_north = document.getElementById("light_north_t1");
    // var t2 = document.getElementById("t2");
    
    // var t1_content = document.createTextNode(`North to South and South to North is ${state_to_color[values["t1"]]}`);
    // var t2_content = document.createTextNode(`East to West and West to East is ${state_to_color[values["t2"]]}`);

    // t1.innerHTML = '';
    // t2.innerHTML = '';
    // t1.appendChild(t1_content);
    // t2.appendChild(t2_content);

    var laneDiv = document.getElementById("lanes");
    for (const [laneId, numCars] of Object.entries(numCarsDict)){
        laneElem = laneDiv.querySelector(`#${laneId}`);
        laneElem.s
        if (laneElem == null){
            laneElem = document.createElement("h2");
            laneElem.setAttribute("id", laneId);
            laneDiv.appendChild(laneElem);
        }
        else{
            laneElem.innerHTML = ``;
        }
        laneElem.setAttribute("class", "lane_info");
        laneElem.setAttribute("color", )       
        laneElem.appendChild(document.createTextNode(`${laneNames[laneId]}\n${numCars} 🚗`));
    }
});

async function main() {
    // start the signalR connection
    start()
    
}

function simulate(){
    var simulateUrl = "http://localhost:7071/api/Simulate";
    // var simulateUrl = "https://smarthighwayfunctionapp.azurewebsites.net/api/Simulate?";
    $.ajax(simulateUrl, {
    type: 'GET',
    data: {
      num_times: 1
    }
  });
}

window.onload = function() {
    var btn = document.getElementById("simulateBtn");
    btn.onclick = simulate;
    main();
}
