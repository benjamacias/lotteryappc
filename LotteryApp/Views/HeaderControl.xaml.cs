using System.Windows;
using System.Windows.Controls;
using LotteryApp;

namespace LotteryApp.Views;

public partial class HeaderControl : UserControl
{
    public HeaderControl()
    {
        InitializeComponent();
    }

    private void Clients_Click(object sender, RoutedEventArgs e)
    {
        var w = new MainWindow();
        w.Show();
        Window.GetWindow(this)?.Close();
    }

    private void Debts_Click(object sender, RoutedEventArgs e)
    {
        var w = new DebtsWindow();
        w.Show();
        Window.GetWindow(this)?.Close();
    }

    private void Cash_Click(object sender, RoutedEventArgs e)
    {
        var w = new CashWindow();
        w.Show();
        Window.GetWindow(this)?.Close();
    }

    private void Graphs_Click(object sender, RoutedEventArgs e)
    {
        var w = new GraphsWindow();
        w.Show();
        Window.GetWindow(this)?.Close();
    }
}

