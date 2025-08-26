using System.Linq;
using System.Windows;
using LotteryApp.Data;
using OxyPlot;
using OxyPlot.Axes;
using OxyPlot.Series;

namespace LotteryApp.Views;

public partial class GraphsWindow : Window
{
    private readonly AppDbContext _db = new();

    public GraphsWindow()
    {
        InitializeComponent();
        LoadChart();
    }

    private void LoadChart()
    {
        var model = new PlotModel { Title = "Saldo por cliente" };
        var series = new ColumnSeries();
        var clients = _db.Clients.ToList();
        for (int i = 0; i < clients.Count; i++)
        {
            series.Items.Add(new ColumnItem((double)clients[i].Balance));
        }
        model.Series.Add(series);
        model.Axes.Add(new CategoryAxis { Position = AxisPosition.Bottom, ItemsSource = clients, LabelField = nameof(Models.Client.Name) });
        Plot.Model = model;
    }

    protected override void OnClosed(System.EventArgs e)
    {
        _db.Dispose();
        base.OnClosed(e);
    }
}

