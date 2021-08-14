const signalR = require("@microsoft/signalr");

// const negotiateUrl = "http://localhost:7071/api";
const negotiateUrl = "https://smarthighwayfunctionapp.azurewebsites.net/api";
const lights = {"t1": ["north", "south"], "t2": ["west", "east"]};
const state_to_color = {0: "Red", 1:"Green"};
const laneIds = ["north_t1", "south_t1", "east_t2", "west_t2"];
const laneNames = {"east_t2": "East to West", "west_t2": "West to East",
                    "north_t1": "North to South", "south_t1": "South to North"};


const connection = new signalR.HubConnectionBuilder()
    .withUrl(`${negotiateUrl}`)
    .withAutomaticReconnect()
    .configureLogging(signalR.LogLevel.Information)
    .build();

connection.Headers

async function start() {
    try {
        await connection.start();
        console.assert(connection.state === signalR.HubConnectionState.Connected);
        console.log("SignalR Connected.");
    } catch (err) {
        console.assert(connection.state === signalR.HubConnectionState.Disconnected);
        console.log(err);
        setTimeout(() => start(), 5000);
    }
};


connection.onclose(async () => {
        await start();
});

connection.on("newMessage", (values, numCarsDict) => {
    // delete the message saying to wait
    var msgElem = document.getElementById("message_to_user");
    if (msgElem != null && msgElem.innerHTML != null){
        msgElem.innerHTML = ``;
    }

    for (const [lightId, directions] of Object.entries(lights)){
        for (var i = 0; i < directions.length; i++){
            var direction = directions[i];
            var lightElem = document.getElementById(`light_${direction}_${lightId}`);
            if (typeof(Storage) != "undefined"){
                localStorage.setItem(`light_${direction}_${lightId}`, state_to_color[values[lightId]]);
            }
            var oppositeDirection = directions[1 - i];
            var content = document.createTextNode(`${direction} to ${oppositeDirection} is ${state_to_color[values[lightId]]}`);
            if (lightElem.innerHTML != null){
                lightElem.innerHTML = ``;
            }
            var fontElem = document.createElement("font");
            fontElem.appendChild(content);
            fontElem.setAttribute("color", state_to_color[values[lightId]].toLowerCase());
            lightElem.appendChild(fontElem);
        }
    }

    var laneDiv = document.getElementById("lanes");
    for (const laneId of laneIds){
        var numCars = numCarsDict[laneId]
        laneElem = laneDiv.querySelector(`#${laneId}`);
        if (laneElem == null){
            laneElem = document.createElement("h2");
            laneElem.setAttribute("id", laneId);
            laneDiv.appendChild(laneElem);
        }
        else{
            if (laneElem.innerHTML != null){
                laneElem.innerHTML = ``;
            }
        }
        if (typeof(Storage) != "undefined"){
            localStorage.setItem(laneId, numCars);
        }
        laneElem.setAttribute("class", "lane_info");
        laneElem.appendChild(document.createTextNode(`${laneNames[laneId]}: ${numCars} 🚗`));
    }
});


function loadPreviousData(){
    if (typeof(Storage) == "undefined"){
        console.log("localStorage is not supported");
        return;
    }
    console.log("localStorage is supported!");
    for (const [lightId, directions] of Object.entries(lights)){
        for (var i = 0; i < directions.length; i++){
            var direction = directions[i];
            var color = localStorage.getItem(`light_${direction}_${lightId}`);
            if (color == null){ // was not previously stored
                console.log(`color is not stored for light_${direction}_${lightId}`);
                continue;
            }
            var direction = directions[i];
            var lightElem = document.getElementById(`light_${direction}_${lightId}`);
            console.log(`lightElem = ${lightElem}, light_${direction}_${lightId}`);
            var oppositeDirection = directions[1 - i];
            var content = document.createTextNode(`${direction} to ${oppositeDirection} is ${color}`);
            if (lightElem.innerHTML != null){
                lightElem.innerHTML = ``;
            }            var fontElem = document.createElement("font");
            fontElem.appendChild(content);
            fontElem.setAttribute("color", color.toLowerCase());
            lightElem.appendChild(fontElem);
        }
    }

    var laneDiv = document.getElementById("lanes");
    for (const laneId of laneIds){
        var numCars = localStorage.getItem(laneId);
        if (numCars == null){ // was not previously stored
            continue;
        }
        laneElem = laneDiv.querySelector(`#${laneId}`);
        if (laneElem == null){
            laneElem = document.createElement("h2");
            laneElem.setAttribute("id", laneId);
            laneDiv.appendChild(laneElem);
        }
        else{
            if (laneElem.innerHTML != null){
                laneElem.innerHTML = ``;
            }
        }
        laneElem.setAttribute("class", "lane_info");
        laneElem.appendChild(document.createTextNode(`${laneNames[laneId]}\n${numCars} 🚗`));
    }
    var msgElem = document.getElementById("message_to_user");
    if (msgElem != null && msgElem.innerHTML != null){
        msgElem.innerHTML = ``;
    }
}

async function main() {
    // start the signalR connection
    start();

    loadPreviousData();
    
}

function simulate(){
    // var simulateUrl = "http://localhost:7071/api/Simulate";
    var simulateUrl = "https://smarthighwayfunctionapp.azurewebsites.net/api/Simulate?";
    console.log("starting to simulate...");
    var messageElem = document.getElementById("message_to_user");
    if (messageElem != null){
        if (messageElem.innerHTML != null){
            messageElem.innerHTML = ``;
        }
        messageElem.appendChild(document.createTextNode("Simulating... Please don't exit."));

    }
    $.ajax(simulateUrl, {
    type: 'GET',
    data: {
      num_times: 1
    },
    success: function (data, status, xhr) {   // success callback function
        console.log(data + " " + status);
    },
    error: function (jqXhr, textStatus, errorMessage) { // error callback 
        console.log('Error: ' + errorMessage);
    }
  });
}

window.onload = function() {
    var btn = document.getElementById("simulateBtn");
    btn.onclick = simulate;
    main();
}
