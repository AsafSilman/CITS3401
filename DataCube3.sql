use mydb;
select d.Date,p.ProductName,c.CurrencyName, SUM(o.TotalPriceAUD) TotalQuantitySold from FactOrderFulfilment o
right outer join DimCurrency c on o.CurrencyKey=c.CurrencyId
right outer join DimDate d on o.OrderDate=d.DateID
right outer join DimProduct p on o.ProductKey=p.ProductID
GROUP BY CUBE(d.Date, p.ProductName, c.CurrencyName);