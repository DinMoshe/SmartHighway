using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Azure.Devices.Client;
using Newtonsoft.Json;
using System.Threading;
using System.IO;

namespace SimulatedDevice
{

    class Program
    {

        private const string DeviceConnectionString = @"HostName=SkeletonHub.azure-devices.net;DeviceId=MyCDevice;SharedAccessKey=ra3mlKw19PB479r5oOLjQyJQNJcQ6wK2NQVecIt1ptI=";

        private static readonly DeviceClient Client = DeviceClient.CreateFromConnectionString(DeviceConnectionString);

        private static string trafficLightId = "0";
        private static int lightState = 0;

        static async Task Main(string[] args)
        {

            Console.WriteLine($"Traffic light id: {trafficLightId}");
            Console.WriteLine();
            

            ReceiveCloudMessages();

        }



        private static async void ReceiveCloudMessages()
        {
            Message receivedMessage;
            while (true)
            {
                try
                {
                    receivedMessage = await Client.ReceiveAsync();
                    if (receivedMessage != null)
                    {
                        string encodedMessage = Encoding.ASCII.GetString(receivedMessage.GetBytes());
                        // format of message is a dictionary lightId -> state
                        var values = JsonConvert.DeserializeObject<Dictionary<string, string>>(encodedMessage);
                        lightState = int.Parse(values[trafficLightId]);
                        if (lightState == 0){  // the traffic light is red
                            Console.ForegroundColor = ConsoleColor.Red;
                            Console.WriteLine("Red");
                        }
                        else
                        {
                            Console.ForegroundColor = ConsoleColor.Green;
                            Console.WriteLine("Green");
                        }

                        await Client.CompleteAsync(receivedMessage);
                    }
                    else
                    {
                        continue;
                    }
                }
                catch{
                    continue;
                }
                
            }
        }
    }
}