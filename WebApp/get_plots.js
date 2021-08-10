const { BlobServiceClient } = require("@azure/storage-blob");
// const accountName = "storageaccounttraffafbc";
const containerName = "plots";

async function main(){
    console.log('Azure Blob storage v12 - JavaScript quickstart sample');

    // Quick start code goes here

    // const blobSasUrl = "https://storageaccounttraffafbc.blob.core.windows.net/?sv=2020-08-10&ss=bfqt&srt=sco&sp=rwdlacupix&se=2021-08-11T22:18:39Z&st=2021-08-07T14:18:39Z&spr=https,http&sig=EeZPm16sfxVvP2KVCWxo0wRxPJoxil0uNq%2F0bhLe2tQ%3D";
    const blobSasUrl = "https://storageaccounttraffafbc.blob.core.windows.net/?sv=2020-08-04&ss=bfqt&srt=sco&sp=rwdlacupx&se=2021-08-12T00:11:15Z&st=2021-08-10T16:11:15Z&spr=https,http&sig=%2FO5aQZbZzfzJM%2F1akc6A5Buvp2o0uT45AUjuzrdRFeo%3D";

    // Create the BlobServiceClient object which will be used to create a container client
    const blobServiceClient = new BlobServiceClient(blobSasUrl);

    // Get a reference to a container
    const containerClient = blobServiceClient.getContainerClient(containerName);

    console.log('\nListing blobs...');

    var divPlots = document.getElementById("trafficPlots");
    divPlots.innerHTML = ``;
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
        img.setAttribute("class", "plot_design");

        divPlots.appendChild(img);
    }
}

window.onload = function() {
    // to activate the main through a button, uncomment these
    // var btn = document.getElementById("myButton");
    // btn.onclick = main;
    main();
}