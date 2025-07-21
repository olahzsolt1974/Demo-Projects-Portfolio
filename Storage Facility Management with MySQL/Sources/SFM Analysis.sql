SELECT	sub.warehouseCode,
		sub.totalQuantityInStockPerWarehouse,
        ware.warehousePctCap as warehouseUsagePercentOfTotalCapacity,
        sub.totalQuantityInStockPerWarehouse / sub.totalQuantityInStockOverAll * 100 AS warehouseStockRatioOverall
FROM (	SELECT	prod.warehouseCode,
		SUM(prod.quantityInStock) AS totalQuantityInStockPerWarehouse,
		(	SELECT SUM(prod.quantityInStock)
			FROM mintclassics.products AS prod	) AS totalQuantityInStockOverAll
		FROM mintclassics.products AS prod
		GROUP BY prod.warehouseCode	) AS sub
        inner join	mintclassics.warehouses as ware on ware.warehouseCode = sub.warehouseCode;
-- Explanation: Presentation.pdf/1.	Warehouse Inventory and Utilization Analysis
-- Result excel sheet name: SFM Diagrams.xlsx/01 Total Quantity by Warehouse

select	cust.customerNumber,
		cust.customerName,
		sum((ordd.quantityOrdered * ordd.priceEach)) as totalOrderedValue
from	mintclassics.orderDetails ordd
		inner join mintclassics.orders as ords on ordd.orderNumber = ords.orderNumber
		inner join mintclassics.customers AS cust on cust.customerNumber = ords.customerNumber
group by	cust.customerNumber,
			cust.customerName
order by 	sum((ordd.quantityOrdered * ordd.priceEach)) desc
limit		10;
-- Explanation: Presentation.pdf/2.	Top 10 Customers by Total Order Value
-- Result excel sheet name: SFM Diagrams.xlsx/02 Top 10 Customers

select	DATE_FORMAT(ords.orderDate, '%Y-%m') as yearMonth,
		sum( case when cust.customerNumber = 141 then (ordd.quantityOrdered * ordd.priceEach) else 0 end) as totalOrderedValueEuroPlus,
        sum( case when cust.customerNumber = 124 then (ordd.quantityOrdered * ordd.priceEach) else 0 end) as totalOrderedValueMinGifts,
        sum( case when cust.customerNumber = 114 then (ordd.quantityOrdered * ordd.priceEach) else 0 end) as totalOrderedValueAustralianCollectors,
        sum( case when cust.customerNumber = 151 then (ordd.quantityOrdered * ordd.priceEach) else 0 end) as totalOrderedValueMuscleMacine,
        sum( case when cust.customerNumber = 119 then (ordd.quantityOrdered * ordd.priceEach) else 0 end) as totalOrderedValueLaRochelle
from	mintclassics.orderDetails ordd
		inner join mintclassics.orders as ords on ordd.orderNumber = ords.orderNumber
		inner join mintclassics.customers AS cust on cust.customerNumber = ords.customerNumber
group by	DATE_FORMAT(ords.orderDate, '%Y-%m')
order by 	DATE_FORMAT(ords.orderDate, '%Y-%m');
-- Explanation: Presentation.pdf/3.	Monthly Sales Trends for Key Customers
-- Result excel sheet name: SFM Diagrams.xlsx/03 Trends of Top 5 Customers

select	prod.productLine,
		sum((ordd.quantityOrdered * ordd.priceEach)) as totalOrderedValue
from	mintclassics.orderDetails ordd
		inner join mintclassics.products AS prod on prod.productCode = ordd.productCode
group by	prod.productLine
order by 	sum((ordd.quantityOrdered * ordd.priceEach)) desc;
-- Explanation: Presentation.pdf/4.	Total Sales by Product Line
-- Result excel sheet name: SFM Diagrams.xlsx/04 Ranking Product Lines

select	DATE_FORMAT(ords.orderDate, '%Y-%m') as yearMonth,
		sum( case when prod.productLine = "Classic Cars" then (ordd.quantityOrdered * ordd.priceEach) else 0 end) as totalOrderedValueClassicCars,
        sum( case when prod.productLine = "Vintage Cars" then (ordd.quantityOrdered * ordd.priceEach) else 0 end) as totalOrderedValueVintageCars,
        sum( case when prod.productLine = "Motorcycles" then (ordd.quantityOrdered * ordd.priceEach) else 0 end) as totalOrderedValueMotorcycles,
        sum( case when prod.productLine = "Trucks and Buses" then (ordd.quantityOrdered * ordd.priceEach) else 0 end) as totalOrderedValueTrucksandBuses,
        sum( case when prod.productLine = "Planes" then (ordd.quantityOrdered * ordd.priceEach) else 0 end) as totalOrderedValuePlanes,
        sum( case when prod.productLine = "Ships" then (ordd.quantityOrdered * ordd.priceEach) else 0 end) as totalOrderedValueShips,
        sum( case when prod.productLine = "Trains" then (ordd.quantityOrdered * ordd.priceEach) else 0 end) as totalOrderedValueTrains,
        sum(ordd.quantityOrdered * ordd.priceEach) as totalOrderedGrandTotal
from	mintclassics.orderDetails ordd
		inner join mintclassics.products AS prod on prod.productCode = ordd.productCode
        inner join mintclassics.orders as ords on ordd.orderNumber = ords.orderNumber
group by	DATE_FORMAT(ords.orderDate, '%Y-%m')
order by 	DATE_FORMAT(ords.orderDate, '%Y-%m');
-- Explanation: Presentation.pdf/5.	Monthly Sales Trends by Product Line
-- Result excel sheet name: SFM Diagrams.xlsx/05 Trends of Product Lines

create view mintclassics.countOfOrderedProductLinesByCustomers as
select	cust.customerNumber,
		cust.customerName,
        count(distinct prod.productLine) as countOfOrderedProductLines
from	mintclassics.customers as cust
		inner join mintclassics.orders as ords on ords.customerNumber = cust.customerNumber
        inner join mintclassics.orderDetails as ordd on ords.orderNumber = ordd.orderNumber
        inner join mintclassics.products as prod on prod.productCode = ordd.productCode
group by	cust.customerNumber,
			cust.customerName
order by	count(distinct prod.productLine) desc;
-- Explanation: Presentation.pdf/

select	*
from	mintclassics.countOfOrderedProductLinesByCustomers;
-- Explanation: Presentation.pdf/6.	Customer Diversity in Product Line Orders
-- Result excel sheet name: SFM Diagrams.xlsx/06 Ordered Prod Lines by Custom

select	countOfOrderedProductLines,
		count(*) as countOfDataInBin
from	mintclassics.countOfOrderedProductLinesByCustomers
group by countOfOrderedProductLines
order by countOfOrderedProductLines;
-- Explanation: Presentation.pdf/7.	Distribution of Customer Product Line Diversity
-- Result excel sheet name: SFM Diagrams.xlsx/07 Distr of Ordered Prod Lines