using System;
using System.Linq;
using LotteryApp.Models;

namespace LotteryApp.Data;

public static class DbInitializer
{
    public static void EnsureCreatedAndSeed(AppDbContext db)
    {
        db.Database.EnsureCreated();
        if (!db.Clients.Any())
        {
            var c1 = new Client { Name = "Juan Perez", Document = "DNI 12345678", Phone = "351-555-1234" };
            var c2 = new Client { Name = "Maria Gomez", Document = "DNI 23456789" };
            db.Clients.AddRange(c1, c2);
            db.SaveChanges();

            db.Debts.Add(new Debt { ClientId = c1.Id, Date = DateTime.Today.AddDays(-5), Amount = 5000m, Description = "Jugadas semana 1" });
            db.Debts.Add(new Debt { ClientId = c1.Id, Date = DateTime.Today.AddDays(-2), Amount = 3000m, Description = "Jugadas semana 2" });
            db.Payments.Add(new Payment { ClientId = c1.Id, Date = DateTime.Today.AddDays(-1), Amount = 4000m, Method = "Efectivo" });

            db.Debts.Add(new Debt { ClientId = c2.Id, Date = DateTime.Today.AddDays(-3), Amount = 2000m, Description = "Jugadas" });
            db.SaveChanges();
        }
    }
}
