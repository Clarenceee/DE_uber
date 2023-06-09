import pandas as pd
import json

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(data, *args, **kwargs):
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your transformation logic here
    df = data
    df = df.drop_duplicates().reset_index(drop=True)
    df['trip_id'] = df.index

    df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])
    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])

    datetime_dim = df[['tpep_pickup_datetime', 'tpep_dropoff_datetime']]
    datetime_dim['pick_hour'] = datetime_dim['tpep_pickup_datetime'].dt.hour
    datetime_dim['pick_day'] = datetime_dim['tpep_pickup_datetime'].dt.day
    datetime_dim['pick_month'] = datetime_dim['tpep_pickup_datetime'].dt.month
    datetime_dim['pick_year'] = datetime_dim['tpep_pickup_datetime'].dt.year
    datetime_dim['pick_weekday'] = datetime_dim['tpep_pickup_datetime'].dt.weekday

    datetime_dim['drop_hour'] = datetime_dim['tpep_dropoff_datetime'].dt.hour
    datetime_dim['drop_day'] = datetime_dim['tpep_dropoff_datetime'].dt.day
    datetime_dim['drop_month'] = datetime_dim['tpep_dropoff_datetime'].dt.month
    datetime_dim['drop_year'] = datetime_dim['tpep_dropoff_datetime'].dt.year
    datetime_dim['drop_weekday'] = datetime_dim['tpep_dropoff_datetime'].dt.weekday

    datetime_dim['datetime_id'] = datetime_dim.index
    datetime_dim = datetime_dim[['datetime_id', 'tpep_pickup_datetime', 'tpep_dropoff_datetime', 'pick_hour', 'pick_day', 'pick_month', 'pick_year', 'pick_weekday', 'drop_hour', 'drop_day', 'drop_month', 'drop_year', 'drop_weekday']]

    passenger_count_dim = df[['passenger_count']].drop_duplicates().reset_index(drop=True)
    passenger_count_dim['passenger_count_id']  = passenger_count_dim.index
    passenger_count_dim = passenger_count_dim[['passenger_count_id','passenger_count']]

    trip_distance_dim = df[['trip_distance']].drop_duplicates().sort_values('trip_distance').reset_index(drop=True)
    trip_distance_dim['trip_distance_id'] = trip_distance_dim.index
    trip_distance_dim = trip_distance_dim[['trip_distance_id', 'trip_distance']]

    rate_code_dict = {
        1: "Standard Rate",
        2: "JFK",
        3: "Newark",
        4: "Nassau or Westchester",
        5: "Negotiated Fare",
        6: "Group Ride"
    }

    rate_code_dim = df[['RatecodeID']].drop_duplicates().reset_index(drop=True)
    rate_code_dim['rate_code_id'] = rate_code_dim.index
    rate_code_dim['rate_code_name'] = rate_code_dim['RatecodeID'].map(rate_code_dict)
    rate_code_dim = rate_code_dim[['rate_code_id', 'RatecodeID', 'rate_code_name']]


    payment_method_dic ={
        1: "Credit Card",
        2: "Cash",
        3: "No Charge",
        4: "Dispute",
        5: "Unknown", 
        6: "Voided Trip"
    }
    payment_method_dim  = df[['payment_type']].drop_duplicates().reset_index(drop=True)
    payment_method_dim['payment_method_id'] = payment_method_dim.index
    payment_method_dim['payment_type_name'] = payment_method_dim['payment_type'].map(payment_method_dic)
    payment_method_dim = payment_method_dim[['payment_method_id', 'payment_type', 'payment_type_name']]

    location_dic = pd.read_csv(r'D:\My Project\DE_uber\Dataset\taxi+_zone_lookup.csv')

    pickup_location_dim = df[['PULocationID']].drop_duplicates().sort_values('PULocationID').reset_index(drop=True)
    pickup_location_dim['pickup_location_id'] = pickup_location_dim.index
    pickup_location_dim['pickup_borough'] = pickup_location_dim['PULocationID'].map(location_dic.set_index('LocationID')['Borough'])
    pickup_location_dim['pickup_zone'] = pickup_location_dim['PULocationID'].map(location_dic.set_index('LocationID')['Zone'])
    pickup_location_dim['pickup_service_zone'] = pickup_location_dim['PULocationID'].map(location_dic.set_index('LocationID')['service_zone'])
    
    dropoff_location_dim = df[['DOLocationID']].drop_duplicates().sort_values('DOLocationID').reset_index(drop=True)
    dropoff_location_dim['dropoff_location_id'] = dropoff_location_dim.index
    dropoff_location_dim['dropoff_borough'] = dropoff_location_dim['DOLocationID'].map(location_dic.set_index('LocationID')['Borough'])
    dropoff_location_dim['dropoff_zone'] = dropoff_location_dim['DOLocationID'].map(location_dic.set_index('LocationID')['Zone'])
    dropoff_location_dim['dropoff_service_zone'] = dropoff_location_dim['DOLocationID'].map(location_dic.set_index('LocationID')['service_zone'])


    fact_table = df.merge(passenger_count_dim, on='passenger_count') \
            .merge(trip_distance_dim, on='trip_distance') \
            .merge(rate_code_dim, on='RatecodeID') \
            .merge(pickup_location_dim, on='PULocationID') \
            .merge(dropoff_location_dim, on='DOLocationID') \
            .merge(datetime_dim, on='tpep_dropoff_datetime') \
            .merge(payment_method_dim, on='payment_type') \
    [['VendorID', 'datetime_id', 'passenger_count_id', 'trip_distance_id', 'rate_code_id', 'pickup_location_id', 'dropoff_location_id', 'payment_method_id',
    'store_and_fwd_flag', 'fare_amount', 'extra','mta_tax', 'tip_amount', 'tolls_amount', 'improvement_surcharge',
        'total_amount', 'congestion_surcharge', 'airport_fee']]

    json_payment = payment_method_dim.to_json(orient='records')
    json_fact = fact_table.to_json(orient='records')
    result = {
        'fact': json.loads(json_fact),
        'payment': json.loads(json_payment)
    }
    return result


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
