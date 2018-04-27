use mydb;
select d.Date,p.ProductName,w.WarehouseName, AVG(fs.StockLevel) AverageStock from FactStockLevels fs
right outer join DimWarehouse w on fs.WarehouseID=w.WarehouseId
right outer join DimDate d on fs.DateID=d.DateID
right outer join DimProduct p on fs.ProductId=p.ProductID
GROUP BY CUBE(d.Date, p.ProductName, w.WarehouseName);