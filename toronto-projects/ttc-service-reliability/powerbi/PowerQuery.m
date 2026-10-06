// Power BI Power Query starter. Run src/analyze.py first to create data/clean_delays.csv.
// Change the path to your local project folder before loading.
let
    Source = Csv.Document(File.Contents("data/clean_delays.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Headers, {
        {"date", type date}, {"time", type time}, {"day_of_week", type text},
        {"station", type text}, {"code", type text}, {"delay_min", Int64.Type},
        {"gap_min", Int64.Type}, {"bound", type text}, {"line", type text},
        {"vehicle", type text}, {"hour", Int64.Type}, {"month", type text}
    }),
    AddDateKey = Table.AddColumn(Types, "DateKey", each Date.ToText([date], "yyyyMMdd"), type text)
in
    AddDateKey
