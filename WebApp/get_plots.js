// import { BlobServiceClient } from '@azure/storage-blob';
const { BlobServiceClient } = require("@azure/storage-blob");

async function main() {
    console.log('Azure Blob storage v12 - JavaScript quickstart sample');
    
    // Quick start code goes here
    const AZURE_STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=storageaccounttraffafbc;AccountKey=+gMPGEjh1jZOX2G5THqKQJRO2LRN7khLUddPQuilaxkHpmJtOilCd36s/zNY/zDwlseUOIFhqa5snpW/t3r5tw==;EndpointSuffix=core.windows.net";
    
    // Create the BlobServiceClient object which will be used to create a container client
    const blobServiceClient = BlobServiceClient.fromConnectionString(AZURE_STORAGE_CONNECTION_STRING);

    
    // Create a unique name for the container
    const containerName = "plots";

    console.log('\nCreating container...');
    console.log('\t', containerName);

    // Get a reference to a container
    const containerClient = blobServiceClient.getContainerClient(containerName);

    // Create the container
    const createContainerResponse = await containerClient.createIfNotExists();
    console.log("Container was created successfully. requestId: ", createContainerResponse.requestId);


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

        var img = new Image();

        img.src = uri;
        divPlots.appendChild(img);

        // const downloadBlockBlobResponse = await blobClient.download(0);
        // console.log('\nDownloaded blob content...');
        // console.log('\t', await streamToString(downloadBlockBlobResponse.readableStreamBody));
    }
    
}

window.onload = function() {
    var btn = document.getElementById("myButton");
    btn.onclick = main;
}
// main().then(() => console.log('Done')).catch((ex) => console.log(ex.message));