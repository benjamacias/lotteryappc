using System;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using LotteryApp.Data;
using LotteryApp.Models;
using Microsoft.EntityFrameworkCore;

namespace LotteryApp;

public partial class MainWindow : Window
{
    private readonly AppDbContext _db = new();

    public MainWindow()
    {
        InitializeComponent();
        DbInitializer.EnsureCreatedAndSeed(_db);
        LoadClients();
    }

    protected override void OnClosed(EventArgs e)
    {
        _db.Dispose();
        base.OnClosed(e);
    }

    private void LoadClients(string? filter = null)
    {
        var query = _db.Clients
            .Include(c => c.Debts)
            .Include(c => c.Payments)
            .AsQueryable();

        if (!string.IsNullOrWhiteSpace(filter))
        {
            var f = filter.Trim().ToLower();
            query = query.Where(c =>
                c.Name.ToLower().Contains(f) ||
                (c.Document != null && c.Document.ToLower().Contains(f)) ||
                (c.Phone != null && c.Phone.ToLower().Contains(f)));
        }

        ClientsGrid.ItemsSource = query
            .OrderBy(c => c.Name)
            .ToList();

        UpdateSelectionDetails();
    }

    private Client? SelectedClient => ClientsGrid.SelectedItem as Client;

    private void UpdateSelectionDetails()
    {
        if (SelectedClient == null)
        {
            DebtsGrid.ItemsSource = null;
            PaymentsGrid.ItemsSource = null;
            BalanceLabel.Text = "Saldo: —";
            return;
        }
        DebtsGrid.ItemsSource = SelectedClient.Debts.OrderByDescending(d => d.Date).ToList();
        PaymentsGrid.ItemsSource = SelectedClient.Payments.OrderByDescending(p => p.Date).ToList();
        BalanceLabel.Text = $"Saldo: {SelectedClient.Balance:C}";
    }

    private void ClientsGrid_SelectionChanged(object sender, SelectionChangedEventArgs e) => UpdateSelectionDetails();

    private void SearchBox_KeyUp(object sender, System.Windows.Input.KeyEventArgs e) => LoadClients(SearchBox.Text);

    private void NewClient_Click(object sender, RoutedEventArgs e)
    {
        var w = new Views.ClientWindow();
        if (w.ShowDialog() == true)
        {
            var c = new Client { Name = w.ClientName, Document = w.Document, Phone = w.Phone, Address = w.Address };
            _db.Clients.Add(c);
            _db.SaveChanges();
            LoadClients(SearchBox.Text);
            SelectClientById(c.Id);
        }
    }

    private void EditClient_Click(object sender, RoutedEventArgs e)
    {
        if (SelectedClient == null) return;
        var c = SelectedClient;
        var w = new Views.ClientWindow(c.Name, c.Document, c.Phone, c.Address);
        if (w.ShowDialog() == true)
        {
            c.Name = w.ClientName;
            c.Document = w.Document;
            c.Phone = w.Phone;
            c.Address = w.Address;
            _db.SaveChanges();
            LoadClients(SearchBox.Text);
            SelectClientById(c.Id);
        }
    }

    private void DeleteClient_Click(object sender, RoutedEventArgs e)
    {
        if (SelectedClient == null) return;
        var res = MessageBox.Show($"Eliminar {SelectedClient.Name}? Se borrarán deudas y pagos.", "Confirmar", MessageBoxButton.YesNo, MessageBoxImage.Warning);
        if (res != MessageBoxResult.Yes) return;
        _db.Clients.Remove(SelectedClient);
        _db.SaveChanges();
        LoadClients(SearchBox.Text);
    }

    private void AddDebt_Click(object sender, RoutedEventArgs e)
    {
        if (SelectedClient == null) return;
        var w = new Views.MoneyWindow("Nueva deuda", "Detalle");
        if (w.ShowDialog() == true)
        {
            _db.Debts.Add(new Debt { ClientId = SelectedClient.Id, Date = w.When, Amount = w.Amount, Description = w.Detail });
            _db.SaveChanges();
            ReloadClient(SelectedClient.Id);
        }
    }

    private void AddPayment_Click(object sender, RoutedEventArgs e)
    {
        if (SelectedClient == null) return;
        var w = new Views.MoneyWindow("Nuevo pago", "Medio");
        if (w.ShowDialog() == true)
        {
            _db.Payments.Add(new Payment { ClientId = SelectedClient.Id, Date = w.When, Amount = w.Amount, Method = w.Detail });
            _db.SaveChanges();
            ReloadClient(SelectedClient.Id);
        }
    }

    private void ReloadClient(int id)
    {
        LoadClients(SearchBox.Text);
        SelectClientById(id);
    }

    private void SelectClientById(int id)
    {
        var list = ClientsGrid.Items.Cast<object>().ToList();
        foreach (var item in list)
        {
            if (item is Client c && c.Id == id)
            {
                ClientsGrid.SelectedItem = item;
                ClientsGrid.ScrollIntoView(item);
                break;
            }
        }
    }
}
