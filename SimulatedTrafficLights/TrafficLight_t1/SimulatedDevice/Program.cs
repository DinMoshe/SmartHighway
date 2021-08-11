using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.AspNetCore.SignalR.Client;


namespace SimulatedDevice
{

    class Program
    {

        private static string trafficLightId = "t1";
        private static int lightState = 0;

        private static string connectionUrl = "https://smarthighwayfunctionapp.azurewebsites.net/api";
        // private static string connectionUrl = "http://localhost:7071/api";
        private static HubConnection hubConnection;

        static async Task Main(string[] args)
        {

            hubConnection = new HubConnectionBuilder()
                            .WithUrl(connectionUrl)
                            .Build();

            hubConnection.Closed += async (error) =>
            {
                await Task.Delay(new Random().Next(0, 5) * 1000);
                await hubConnection.StartAsync();
            };

            hubConnection.On<Dictionary<string, int>>("newMessage", (values) =>
            {
                lightState = values[trafficLightId];
                if (lightState == 0)
                {  // the traffic light is red
                    Console.ForegroundColor = ConsoleColor.Red;
                    Console.WriteLine("Red");
                }
                else
                {
                    Console.ForegroundColor = ConsoleColor.Green;
                    Console.WriteLine("Green");
                }
            });


            while (true)
            {
                try
                {
                    await hubConnection.StartAsync();
                }
                catch
                {
                    continue;
                }
            }

        }

    }
}