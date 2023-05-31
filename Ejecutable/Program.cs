using System;
using System.Diagnostics;
using System.Runtime.InteropServices;

class Program
{

    static void Main()
    {
        Process process3 = StartProcess("cmd", "/c concurrently \"start C:\\api\\API_ProyectoFinal.exe\" \"serve -s build\" \"electron http://127.0.0.1:3000\"");

        process3.EnableRaisingEvents = true;
        process3.Exited += (sender, e) => ExitApplication();

        // Finalizar la aplicación
        Environment.Exit(0);
    }

    static Process StartProcess(string command, string arguments = "")
    {
        ProcessStartInfo startInfo = new ProcessStartInfo();
        startInfo.FileName = command;
        startInfo.Arguments = arguments;
        startInfo.CreateNoWindow = true;
        startInfo.UseShellExecute = false;

        Process process = new Process();
        process.StartInfo = startInfo;
        process.Start();

        return process;
    }

    static void ExitApplication()
    {
        Environment.Exit(0);
    }
}
