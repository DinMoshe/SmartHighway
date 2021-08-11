var azure = require('azure-storage');

const containerName = "plots";
const blobNames = ["east_t2_plot.png", "west_t2_plot.png", "south_t1_plot.png", "north_t1_plot.png"];
const storageConnString = "DefaultEndpointsProtocol=https;AccountName=storageaccounttraffafbc;AccountKey=+gMPGEjh1jZOX2G5THqKQJRO2LRN7khLUddPQuilaxkHpmJtOilCd36s/zNY/zDwlseUOIFhqa5snpW/t3r5tw==;EndpointSuffix=core.windows.net";

function getSasUrl(blobName, containerName){
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

}

window.onload = function() {
    main();
}