using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace LotteryApp.Models;

public class CashMovement
{
    public int Id { get; set; }

    [Required]
    public DateTime Date { get; set; } = DateTime.Now;

    [Column(TypeName = "decimal(18,2)")]
    public decimal Amount { get; set; }

    [MaxLength(240)]
    public string? Description { get; set; }
}
