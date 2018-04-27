use mydb;
select d.Date,p.ProductName,g.EnglishCountryRegionName, SUM(o.Quantity) TotalQuantitySold from FactOrderFulfilment o
right outer join DimGeography g on o.GeographyKey=g.GeographyId
right outer join DimDate d on o.OrderDate=d.DateID
right outer join DimProduct p on o.ProductKey=p.ProductID
GROUP BY CUBE(d.Date, p.ProductName, g.EnglishCountryRegionName);