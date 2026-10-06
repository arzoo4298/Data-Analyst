// Power BI Power Query starter. Run src/analyze.py first to create data/clean_site_month.csv.
// Missing charges remain null by design. Change the path to your local project folder.
let
    Source = Csv.Document(File.Contents("data/clean_site_month.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Headers, {
        {"site_instance_id", type text}, {"site_code", type text}, {"location", type text},
        {"ward", type text}, {"enforcement_start", type date}, {"enforcement_end", type date},
        {"month", type date}, {"charges", Int64.Type}
    })
in
    Types
