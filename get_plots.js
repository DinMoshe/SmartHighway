const { BlobServiceClient } = require("@azure/storage-blob");

// Load the .env file if it exists
// const dotenv = require("dotenv").config();

const accountName = "storageaccounttraffafbc";
const containerName = "plots";
const blobNames = ["east_t2_plot.png", "west_t2_plot.png", "south_t1_plot.png", "north_t1_plot.png"];
const storageConnString = "DefaultEndpointsProtocol=https;AccountName=storageaccounttraffafbc;AccountKey=+gMPGEjh1jZOX2G5THqKQJRO2LRN7khLUddPQuilaxkHpmJtOilCd36s/zNY/zDwlseUOIFhqa5snpW/t3r5tw==;EndpointSuffix=core.windows.net";
const accessKey = "+gMPGEjh1jZOX2G5THqKQJRO2LRN7khLUddPQuilaxkHpmJtOilCd36s/zNY/zDwlseUOIFhqa5snpW/t3r5tw==";

function getSasUrl(blobName, containerName){
    var azure = require('azure-storage');
    var blobService = azure.createBlobService(storageAccountOrConnectionString=storageConnString);

    var startDate = new Date();
    var expiryDate = new Date(startDate);
    expiryDate.setMinutes(startDate.getMinutes() + 100);
    startDate.setMinutes(startDate.getMinutes() - 100);

    var sharedAccessPolicy = {
    AccessPolicy: {
        Permissions: azure.BlobUtilities.SharedAccessPermissions.READ,
        Start: startDate,
        Expiry: expiryDate
        }
    };

    var token = blobService.generateSharedAccessSignature(containerName, blobName, sharedAccessPolicy);
    var sasUrl = blobService.getUrl(containerName, blobName, token);
    return sasUrl;
}

async function main(){
    console.log('Azure Blob storage v12 - JavaScript quickstart sample');
    var divPlots = document.getElementById("trafficPlots");
    divPlots.innerHTML = ``;

    console.log(`\nListing blobs...`);
    for (const blobName of blobNames){
        console.log('\n', blobName);
        var sasUrl = getSasUrl(blobName, containerName);

        // create img element to display the blob
        var uri = sasUrl;
        var img = document.createElement("img");
        img.setAttribute("src", uri);
        img.setAttribute("class", "plot_design");
        img.setAttribute("width", "400");
        img.setAttribute("height", "300");

        divPlots.appendChild(img);
    }

    // const blobSasUrl = "https://storageaccounttraffafbc.blob.core.windows.net/?sv=2020-08-10&ss=bfqt&srt=sco&sp=rwdlacupix&se=2021-08-11T22:18:39Z&st=2021-08-07T14:18:39Z&spr=https,http&sig=EeZPm16sfxVvP2KVCWxo0wRxPJoxil0uNq%2F0bhLe2tQ%3D";
    // const blobSasUrl = "https://storageaccounttraffafbc.blob.core.windows.net/?sv=2020-08-04&ss=bfqt&srt=sco&sp=rwdlacupx&se=2021-08-12T00:11:15Z&st=2021-08-10T16:11:15Z&spr=https,http&sig=%2FO5aQZbZzfzJM%2F1akc6A5Buvp2o0uT45AUjuzrdRFeo%3D";

    // // Create the BlobServiceClient object which will be used to create a container client
    // const blobServiceClient =  new BlobServiceClient(blobSasUrl);

    // // Get a reference to a container
    // const containerClient = blobServiceClient.getContainerClient(containerName);

    // console.log('\nListing blobs...');

    // var divPlots = document.getElementById("trafficPlots");
    // divPlots.innerHTML = ``;
    // // List the blob(s) in the container.
    // for await (const blob of containerClient.listBlobsFlat()) {
    //     console.log('\n', blob.name);
    //     // Get a blob client
    //     const blobClient = containerClient.getBlobClient(blob.name);
    //     var uri = blobClient.url;

    //     var img = document.createElement("img");
    //     img.setAttribute("src", uri);
    //     img.setAttribute("class", "plot_design");

    //     divPlots.appendChild(img);
    // }
}

window.onload = function() {
    main();
}