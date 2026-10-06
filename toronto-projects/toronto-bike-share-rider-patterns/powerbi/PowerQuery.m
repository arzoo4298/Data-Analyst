// Power BI Power Query starter. Run src/analyze.py first to create data/clean_trips.csv.
// Change the path to your local project folder before loading.
let
    Source = Csv.Document(File.Contents("data/clean_trips.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Headers, {
        {"trip_id", type text}, {"start", type datetime}, {"end", type datetime},
        {"trip_minutes", type number}, {"user_type", type text},
        {"start_station_id", type text}, {"start_station", type text},
        {"end_station_id", type text}, {"end_station", type text},
        {"bike_model", type text}, {"month", type text}, {"weekday", type text},
        {"hour", Int64.Type}, {"weekend", type logical}
    }),
    AddTripDate = Table.AddColumn(Types, "TripDate", each Date.From([start]), type date)
in
    AddTripDate
