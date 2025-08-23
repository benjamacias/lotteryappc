using System.Windows;

namespace LotteryApp.Views;

public partial class ClientWindow : Window
{
    public string ClientName => NameBox.Text.Trim();
    public string? Document => string.IsNullOrWhiteSpace(DocBox.Text) ? null : DocBox.Text.Trim();
    public string? Phone => string.IsNullOrWhiteSpace(PhoneBox.Text) ? null : PhoneBox.Text.Trim();
    public string? Address => string.IsNullOrWhiteSpace(AddressBox.Text) ? null : AddressBox.Text.Trim();

    public ClientWindow(string name = "", string? document = null, string? phone = null, string? address = null)
    {
        InitializeComponent();
        NameBox.Text = name;
        DocBox.Text = document ?? "";
        PhoneBox.Text = phone ?? "";
        AddressBox.Text = address ?? "";
    }

    private void Save_Click(object sender, RoutedEventArgs e)
    {
        if (string.IsNullOrWhiteSpace(ClientName))
        {
            MessageBox.Show("Nombre requerido");
            return;
        }
        DialogResult = true;
    }
}
