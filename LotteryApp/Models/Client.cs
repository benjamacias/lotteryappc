using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;

namespace LotteryApp.Models;

public class Client
{
    public int Id { get; set; }

    [Required, MaxLength(120)]
    public string Name { get; set; } = string.Empty;

    [MaxLength(32)]
    public string? Document { get; set; }

    [MaxLength(32)]
    public string? Phone { get; set; }

    [MaxLength(200)]
    public string? Address { get; set; }

    public List<Debt> Debts { get; set; } = new();
    public List<Payment> Payments { get; set; } = new();

    [NotMapped]
    public decimal Balance => (Debts?.Sum(d => d.Amount) ?? 0m) - (Payments?.Sum(p => p.Amount) ?? 0m);
}
