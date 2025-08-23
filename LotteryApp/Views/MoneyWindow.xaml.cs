using System;
using System.Globalization;
using MaterialDesignThemes.Wpf;
using System.Windows;

namespace LotteryApp.Views;

public partial class MoneyWindow : Window
{
    public DateTime When => DateBox.SelectedDate ?? DateTime.Today;
    public decimal Amount { get; private set; }
    public string? Detail => string.IsNullOrWhiteSpace(DetailBox.Text) ? null : DetailBox.Text.Trim();

    public MoneyWindow(string title, string detailPlaceholder)
    {
        InitializeComponent();
        Title = title;
        DateBox.SelectedDate = DateTime.Today;
        HintAssist.SetHint(DetailBox, detailPlaceholder);
    }

    private void Save_Click(object sender, RoutedEventArgs e)
    {
        if (!decimal.TryParse(AmountBox.Text.Replace(",", "."), NumberStyles.Any, CultureInfo.InvariantCulture, out var amount) || amount <= 0)
        {
            MessageBox.Show("Monto inválido");
            return;
        }
        Amount = amount;
        DialogResult = true;
    }
}
