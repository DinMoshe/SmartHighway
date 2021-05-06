using System;
using System.Collections.Generic;
using Microsoft.Azure.CognitiveServices.Vision.ComputerVision;
using Microsoft.Azure.CognitiveServices.Vision.ComputerVision.Models;
using System.Threading.Tasks;
using System.IO;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System.Threading;
using System.Linq;
using RestSharp;


namespace SmartHighway
{

    /* Code taken from:
     * https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/quickstarts-sdk/image-analysis-client-library?success=authenticate-client&tabs=visual-studio&pivots=programming-language-csharp#analyze-an-image
     */
    class ImageProcess
    {
        const string subscriptionKey = "5a2035bfc7184808b2534e736b97c5a4";  // of the computer-vision-iot-project resource
        const string endpoint = "https://computer-vision-iot-project.cognitiveservices.azure.com";
        private static RestClient client = new RestClient(endpoint);
        // URL image used for analyzing an image
        //private const string ANALYZE_URL_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/2011_Toyota_Corolla_--_NHTSA.jpg/330px-2011_Toyota_Corolla_--_NHTSA.jpg";
        private static string ANALYZE_URL_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/5/5d/401_Gridlock.jpg";

        static void Main(string[] args)
        {
            Console.WriteLine("Hello World!");

            // These 2 lines use objects and libraries of Azure Computer Vision to extract data from an image
            ComputerVisionClient client = Authenticate(endpoint, subscriptionKey);
            AnalyzeImageUrl(client, ANALYZE_URL_IMAGE).Wait();

            //Analyze(); // this is a function using HTTP call to the API to get data about the image, our implementation
        }

         /*
         * AUTHENTICATE
         * Creates a Computer Vision client used by each example.
         */
        public static ComputerVisionClient Authenticate(string endpoint, string key)
        {
            ComputerVisionClient client =
              new ComputerVisionClient(new ApiKeyServiceClientCredentials(key))
              { Endpoint = endpoint };
            return client;
        }

        /* 
        * ANALYZE IMAGE - URL IMAGE
        * Analyze URL image. Extracts captions, categories, tags, objects, faces, racy/adult/gory content,
        * brands, celebrities, landmarks, color scheme, and image types.
        */
        public static async Task AnalyzeImageUrl(ComputerVisionClient client, string imageUrl)
        {
            Console.WriteLine("----------------------------------------------------------");
            Console.WriteLine("ANALYZE IMAGE - URL");
            Console.WriteLine();

            // Creating a list that defines the features to be extracted from the image. 

            List<VisualFeatureTypes?> features = new List<VisualFeatureTypes?>()
                {
                    /*VisualFeatureTypes.Categories, VisualFeatureTypes.Description,
                    VisualFeatureTypes.Faces, VisualFeatureTypes.ImageType,
                    VisualFeatureTypes.Tags, VisualFeatureTypes.Adult,
                    VisualFeatureTypes.Color, VisualFeatureTypes.Brands,*/
                    VisualFeatureTypes.Objects
                };

            Console.WriteLine($"Analyzing the image {Path.GetFileName(imageUrl)}...");
            Console.WriteLine();
            // Analyze the URL image 
            ImageAnalysis results = await client.AnalyzeImageAsync(imageUrl, visualFeatures: features);

            // Objects
            Console.WriteLine("Objects:");
            foreach (var obj in results.Objects)
            {
                Console.WriteLine($"{obj.ObjectProperty} with confidence {obj.Confidence} at location {obj.Rectangle.X}, " +
                  $"{obj.Rectangle.X + obj.Rectangle.W}, {obj.Rectangle.Y}, {obj.Rectangle.Y + obj.Rectangle.H}");
            }
            Console.WriteLine();
        }

        private static void Analyze()
        {
            var request = new RestRequest("/vision/v2.1/analyze?visualFeatures=Objects&details=Celebrities&language=en", Method.POST);

            request.AddJsonBody(new
            {
                url = ANALYZE_URL_IMAGE
            });
            
            request.AddHeader("Content-Type", "application/json");
            request.AddHeader("Ocp-Apim-Subscription-Key", subscriptionKey);

            IRestResponse response = client.Execute(request);
            var content = response.Content;

            Console.WriteLine(content);
        }
    }
}
