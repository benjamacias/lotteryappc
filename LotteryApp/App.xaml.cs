using System;
using System.IO;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Threading;

namespace LotteryApp
{
    public partial class App : Application
    {
        public App()
        {
            QuestPDF.Settings.License = QuestPDF.Infrastructure.LicenseType.Community;
            SQLitePCL.Batteries_V2.Init();

            this.DispatcherUnhandledException += OnDispatcherUnhandledException;
            AppDomain.CurrentDomain.UnhandledException += OnUnhandledException;
            TaskScheduler.UnobservedTaskException += OnUnobservedTaskException;
        }

        void Log(string msg)
        {
            try
            {
                var path = Path.Combine(AppContext.BaseDirectory, "error.log");
                File.AppendAllText(path, $"{DateTime.Now:yyyy-MM-dd HH:mm:ss} {msg}{Environment.NewLine}");
            } catch {}
        }

        void OnDispatcherUnhandledException(object s, DispatcherUnhandledExceptionEventArgs e)
        {
            Log(e.Exception.ToString());
            MessageBox.Show(e.Exception.ToString(), "Error");
            e.Handled = true;
        }
        void OnUnhandledException(object s, UnhandledExceptionEventArgs e) => Log(e.ExceptionObject?.ToString() ?? "Unknown");
        void OnUnobservedTaskException(object? s, UnobservedTaskExceptionEventArgs e) { Log(e.Exception.ToString()); e.SetObserved(); }
    }
}
