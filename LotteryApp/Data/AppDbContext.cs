using Microsoft.EntityFrameworkCore;
using LotteryApp.Models;
using System.IO;

namespace LotteryApp.Data;

public class AppDbContext : DbContext
{
    public DbSet<Client> Clients => Set<Client>();
    public DbSet<Debt> Debts => Set<Debt>();
    public DbSet<Payment> Payments => Set<Payment>();

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        var dbPath = Path.Combine(Directory.GetCurrentDirectory(), "lottery.db");
        optionsBuilder.UseSqlite($"Data Source={dbPath}");
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Debt>()
            .HasOne(d => d.Client)
            .WithMany(c => c.Debts)
            .HasForeignKey(d => d.ClientId)
            .OnDelete(DeleteBehavior.Cascade);

        modelBuilder.Entity<Payment>()
            .HasOne(p => p.Client)
            .WithMany(c => c.Payments)
            .HasForeignKey(p => p.ClientId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}
