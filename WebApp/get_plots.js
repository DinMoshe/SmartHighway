const { BlobServiceClient } = require("@azure/storage-blob");
import * as signalR from "@microsoft/signalr";

const accountName = "storageaccounttraffafbc";
const containerName = "plots";
const negotiateUrl = "http://localhost:7071/api/";

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

connection.on("newMessage", (values, num_cars_dict) => {
    var t1 = document.getElementById("t1");
    var t2 = document.getElementById("t2");
    
    var state_to_color = {0: "Red", 1:"Green"};
    var t1_content = document.createTextNode(`${state_to_color[values["t1"]]}`);
    var t2_content = document.createTextNode(`${state_to_color[values["t2"]]}`);

    t1.innerHTML = '';
    t2.innerHTML = '';
    t1.appendChild(t1_content);
    t2.appendChild(t2_content);

    var laneDiv = document.getElementById("lanes");

    for (const [lane_id, num_cars] of Object.entries(num_cars_dict)){
        laneElem = laneDiv.querySelector(`#${lane_id}`);
        if (laneElem == null){
            laneElem = document.createElement("li");
            laneDiv.appendChild(laneElem);
        }
        else{
            laneElem.innerHTML = ``;
        }
        laneElem.appendChild(document.createTextNode(`${num_cars}`));
    }
});

async function main() {
    // start the signalR connection
    start()

    console.log('Azure Blob storage v12 - JavaScript quickstart sample');

    // Quick start code goes here

    const blobSasUrl = "https://storageaccounttraffafbc.blob.core.windows.net/?sv=2020-08-04&ss=bfqt&srt=sco&sp=rwdlacupix&se=2021-08-11T22:18:39Z&st=2021-08-07T14:18:39Z&spr=https,http&sig=EeZPm16sfxVvP2KVCWxo0wRxPJoxil0uNq%2F0bhLe2tQ%3D";
    // Create the BlobServiceClient object which will be used to create a container client
    const blobServiceClient = new BlobServiceClient(blobSasUrl);

    // Get a reference to a container
    const containerClient = blobServiceClient.getContainerClient(containerName);

    console.log('\nListing blobs...');

    var divPlots = document.getElementById("trafficPlots")
    // List the blob(s) in the container.
    for await (const blob of containerClient.listBlobsFlat()) {
        console.log('\n', blob.name);
        // Get blob content from position 0 to the end
        // In Node.js, get downloaded data by accessing downloadBlockBlobResponse.readableStreamBody
        // In browsers, get downloaded data by accessing downloadBlockBlobResponse.blobBody
        // Get a block blob client
        const blobClient = containerClient.getBlobClient(blob.name);
        var uri = blobClient.url;

        var img = document.createElement("img");
        img.setAttribute("src", uri);

        divPlots.appendChild(img);
    }
    
}

window.onload = function() {
    // to activate the main through a button, uncomment these
    // var btn = document.getElementById("myButton");
    // btn.onclick = main;
    main();
}
