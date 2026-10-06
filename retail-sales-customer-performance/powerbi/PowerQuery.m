let
    Source = Csv.Document(
        File.Contents("data/retail_sales_clean.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Headers, {
        {"InvoiceNo", type text}, {"StockCode", type text},
        {"Description", type text}, {"Quantity", Int64.Type},
        {"InvoiceDate", type datetime}, {"UnitPrice", type number},
        {"CustomerID", Int64.Type}, {"Country", type text},
        {"RevenueGBP", type number}
    }),
    OrderDate = Table.AddColumn(Types, "OrderDate", each Date.From([InvoiceDate]), type date),
    MonthStart = Table.AddColumn(OrderDate, "MonthStart", each Date.StartOfMonth([OrderDate]), type date)
in
    MonthStart
