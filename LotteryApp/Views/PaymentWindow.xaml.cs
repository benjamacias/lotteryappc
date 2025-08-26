using System;
using System.Globalization;
using System.Windows;
using System.Windows.Controls;

namespace LotteryApp.Views;

public partial class PaymentWindow : Window
{
    public DateTime When => DateBox.SelectedDate ?? DateTime.Today;
    public decimal Amount { get; private set; }
    public string? Method => (MethodBox.SelectedItem as ComboBoxItem)?.Content?.ToString();
    public string? Notes => string.IsNullOrWhiteSpace(NotesBox.Text) ? null : NotesBox.Text.Trim();

    public PaymentWindow()
    {
        InitializeComponent();
        DateBox.SelectedDate = DateTime.Today;
    }

    private void Save_Click(object sender, RoutedEventArgs e)
    {
        if (!decimal.TryParse(AmountBox.Text.Replace(",", "."), NumberStyles.Any, CultureInfo.InvariantCulture, out var amount) || amount <= 0)
        {
            MessageBox.Show("Monto inválido");
            return;
        }
        if (MethodBox.SelectedItem == null)
        {
            MessageBox.Show("Seleccione un medio de pago");
            return;
        }
        Amount = amount;
        DialogResult = true;
    }
}
