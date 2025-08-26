using System.Linq;
using System.Windows;
using LotteryApp.Data;
using Microsoft.EntityFrameworkCore;

namespace LotteryApp.Views;

public partial class DebtsWindow : Window
{
    private readonly AppDbContext _db = new();

    public DebtsWindow()
    {
        InitializeComponent();
        DebtsGrid.ItemsSource = _db.Debts
            .Include(d => d.Client)
            .OrderByDescending(d => d.Date)
            .ToList();
    }

    protected override void OnClosed(System.EventArgs e)
    {
        _db.Dispose();
        base.OnClosed(e);
    }
}

