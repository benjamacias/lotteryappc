using System;
using System.Linq;
using System.Windows;
using LotteryApp.Data;
using Microsoft.EntityFrameworkCore;

namespace LotteryApp.Views;

public partial class CashWindow : Window
{
    private readonly AppDbContext _db = new();

    public CashWindow()
    {
        InitializeComponent();
        DateBox.SelectedDate = DateTime.Today;
        LoadData();
    }

    private void LoadData()
    {
        var day = DateBox.SelectedDate ?? DateTime.Today;
        var payments = _db.Payments
            .Include(p => p.Client)
            .Where(p => p.Date.Date == day.Date)
            .ToList();
        var withdrawals = _db.CashMovements
            .Where(c => c.Date.Date == day.Date)
            .ToList();
        PaymentsGrid.ItemsSource = payments;
        WithdrawalsGrid.ItemsSource = withdrawals;
        var total = payments.Where(p => p.Method == "Efectivo").Sum(p => p.Amount) - withdrawals.Sum(w => w.Amount);
        TotalLabel.Text = $"Total efectivo: {total:C}";
    }

    private void DateBox_SelectedDateChanged(object sender, System.Windows.Controls.SelectionChangedEventArgs e) => LoadData();

    private void Withdraw_Click(object sender, RoutedEventArgs e)
    {
        var w = new MoneyWindow("Retiro de efectivo", "Detalle");
        if (w.ShowDialog() == true)
        {
            _db.CashMovements.Add(new Models.CashMovement { Date = w.When, Amount = w.Amount, Description = w.Detail });
            _db.SaveChanges();
            LoadData();
        }
    }

    protected override void OnClosed(EventArgs e)
    {
        _db.Dispose();
        base.OnClosed(e);
    }
}
